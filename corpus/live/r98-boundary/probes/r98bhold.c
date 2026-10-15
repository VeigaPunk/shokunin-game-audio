/* r98bstream.c — native pw_stream C-API probe for round 98 (namespace r98b_* (boundary seat, copied from r98-scout probe r98stream.c)).
 *
 * Seat: audio r98 boundary (leaf; probe copied verbatim from the r98 scout probe, namespace only).
 * Purpose: measure the native PipeWire client stream API (libpipewire-0.3,
 * pw_stream_*), which no prior round measured. Every object created by this
 * client carries an r98b_* name; the client never targets a hardware sink for
 * audio (silence only, private null-sink targets).
 *
 * Build: gcc -O2 -o r98bstream r98bstream.c $(pkg-config --cflags --libs libpipewire-0.3) -lm
 *
 * Modes (argv[1]):
 *   info    — core connect + pw_core_info + library version
 *   state   — connect (no autoconnect) and log the state machine
 *   run     — playback stream to a target, N ms, buffer/time accounting
 *   stall   — run + a deliberate process-callback stall (xrun injection)
 *   flags   — connect with a named flag set, report props/threads/state
 *   time    — pw_stream_get_time_n before/after activation
 *   drain   — queue N buffers then pw_stream_flush(drain=true)
 *   neg     — param_changed lattice + pw_stream_update_params mid-stream
 *   props   — connect with arbitrary extra props, report stream props
 *   cap     — capture stream (from a monitor), byte count + first samples
 *   error   — refusal/error-path cases (see err_case)
 *
 * Options (key=value argv[2..]):
 *   target=<node.name|serial>   props=k=v;k=v   flags=a,b,c
 *   ms=<run ms>  stall_at=<cb#>  stall_ms=<ms>  nbuf=<buffers>
 *   rate=<>  channels=<>  fmt=f32|s16  dir=out|in  no_params=1
 *   case=<error case>  name=<client/node name suffix>  hold=<ms>
 *
 * Boundary-seat delta vs the r98-scout probe (r98stream.c): the namespace
 * prefix (r98b_) and the `hold=<ms>` option. hold>0 suppresses the probe's
 * early-quit paths (activate/trigger arms quit the loop ~20 ms after firing,
 * which truncated the scout's activation/trigger observation window); the
 * stream is then observed for the full `hold` window. hold=0 (default) is
 * timing-identical to the scout probe. No other behaviour differs.
 */

#define _GNU_SOURCE
#include <pipewire/pipewire.h>
#include <spa/param/audio/format-utils.h>
#include <spa/param/audio/raw.h>
#include <spa/param/props.h>
#include <spa/debug/pod.h>
#include <spa/utils/result.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <time.h>
#include <math.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/resource.h>

#define MAX_CB_LOG 128

struct data {
	const char *mode;
	struct pw_main_loop *loop;
	struct pw_context *context;
	struct pw_core *core;
	struct pw_stream *stream;
	struct spa_hook core_listener;
	struct spa_hook stream_listener;
	struct spa_source *timer;

	struct pw_core_info *core_info;

	/* options */
	char *target;
	char *extra_props;
	char *flag_str;
	char *err_case;
	char *name;
	int run_ms;
	int stall_at;
	int stall_ms;
	int nbuf;
	int activate_after;
	int trigger_after;
	int drain_at;
	int drain_done;
	int proc_nice;
	int activate_done, trigger_done, trigger_rc;
	int arm_ms;
	int hold;	/* boundary-seat delta: if >0, never take an early quit path
			 * (activate/trigger arms) before t0+hold ms. hold=0 keeps the
			 * scout probe's exact timing behaviour. */
	int rate;
	int channels;
	int fmt_s16;
	int no_params;
	enum pw_direction direction;
	enum pw_stream_flags flags;

	/* capture stats */
	uint64_t cap_frames, cap_nz;
	double cap_peak;
	double cap_rms_sum;
	double g997_re, g997_im, g440_re, g440_im;
	double g997_rot_c, g997_rot_s, g440_rot_c, g440_rot_s;
	double g997_cr, g997_ci, g440_cr, g440_ci;
	uint64_t cap_sample_index;

	/* observed */
	enum pw_stream_state state;
	int connect_rc, disconnect_rc;
	int set_active_rc, set_active2_rc, flush_rc, set_rate_rc, update_params_rc;
	int queue_rc_err, dequeue_null;
	uint64_t t0_ms, t_connect_ms, t_first_cb_ms, t_streaming_ms, t_end_ms;
	uint64_t t_stall_start_ms, t_stall_end_ms;
	uint64_t cb_count, cb_bytes;
	uint64_t cb_log[MAX_CB_LOG];
	int cb_log_n;
	uint32_t last_maxsize, last_chunk_size, last_stride, last_bufid, last_nbufs;
	uint32_t node_id;
	int n_add_buffer, n_remove_buffer, n_drained, n_trigger_done;
	void *alloc_ptrs[64];
	int n_alloc_ptrs;
	int add_buffer_data_null;
	int n_io_changed, n_control_info, n_param_changed;
	int param_ids[16];
	int n_params_seen;
	int fmt_seen;
	uint32_t fmt_format, fmt_rate, fmt_channels;
	struct pw_time ptime;
	int time_rc_before, time_rc_after;
	int is_driving, is_lazy;
	int proc_tid, proc_sched, proc_prio;
	int main_tid, main_sched, main_prio;
	int drained_flag;
	uint64_t first_drained_ms;
	int trigger_count;
	uint64_t flush_ms;
	char error_str[256];
	int stream_error_seen;
};

static uint64_t now_ms(void)
{
	struct timespec ts;
	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (uint64_t)ts.tv_sec * 1000ull + (uint64_t)ts.tv_nsec / 1000000ull;
}

static const char *state_str(enum pw_stream_state s)
{
	return pw_stream_state_as_string(s);
}

static void on_core_info(void *userdata, const struct pw_core_info *info)
{
	struct data *d = userdata;
	d->core_info = pw_core_info_merge(d->core_info, info, true);
}

static void on_core_error(void *userdata, uint32_t id, int seq, int res, const char *message)
{
	struct data *d = userdata;
	(void)id; (void)seq;
	fprintf(stderr, "EV core_error res=%d %s\n", res, message);
	if (!d->stream_error_seen && res < 0) {
		snprintf(d->error_str, sizeof(d->error_str), "core:%s", message);
		d->stream_error_seen = 1;
	}
}

static const struct pw_core_events core_events = {
	PW_VERSION_CORE_EVENTS,
	.info = on_core_info,
	.error = on_core_error,
};

static void on_state_changed(void *userdata, enum pw_stream_state old,
			     enum pw_stream_state state, const char *error)
{
	struct data *d = userdata;
	uint64_t t = now_ms();
	printf("EV state old=%s new=%s error=%s t_ms=%llu\n",
	       state_str(old), state_str(state), error ? error : "-",
	       (unsigned long long)(t - d->t0_ms));
	fflush(stdout);
	d->state = state;
	if (state == PW_STREAM_STATE_STREAMING && d->t_streaming_ms == 0)
		d->t_streaming_ms = t;
	if (state == PW_STREAM_STATE_ERROR && error) {
		snprintf(d->error_str, sizeof(d->error_str), "%s", error);
		d->stream_error_seen = 1;
	}
	if (d->mode && strcmp(d->mode, "state") == 0 &&
	    (state == PW_STREAM_STATE_PAUSED || state == PW_STREAM_STATE_ERROR)) {
		if (d->timer) {
			struct timespec v = { .tv_sec = 0, .tv_nsec = 200 * 1000 * 1000 };
			pw_loop_update_timer(pw_main_loop_get_loop(d->loop), d->timer, &v, NULL, false);
		}
	}
}

static void on_param_changed(void *userdata, uint32_t id, const struct spa_pod *param)
{
	struct data *d = userdata;
	d->n_param_changed++;
	if (d->n_params_seen < 16)
		d->param_ids[d->n_params_seen++] = (int)id;
	if (param == NULL)
		return;
	if (id == SPA_PARAM_Format) {
		struct spa_audio_info_raw info;
		memset(&info, 0, sizeof(info));
		if (spa_format_audio_raw_parse(param, &info) >= 0) {
			d->fmt_seen = 1;
			d->fmt_format = info.format;
			d->fmt_rate = info.rate;
			d->fmt_channels = info.channels;
		}
	}
}

static void log_cb_time(struct data *d, uint64_t t)
{
	if (d->cb_log_n < MAX_CB_LOG)
		d->cb_log[d->cb_log_n++] = t;
}

static void on_process(void *userdata)
{
	struct data *d = userdata;
	uint64_t t = now_ms();
	struct pw_buffer *b;
	struct spa_buffer *buf;

	d->cb_count++;
	if (d->cb_count == 1) {
		d->t_first_cb_ms = t;
		d->proc_tid = (int)syscall(SYS_gettid);
		d->proc_sched = sched_getscheduler(0);
		{
			struct sched_param sp;
			if (sched_getparam(0, &sp) == 0)
				d->proc_prio = sp.sched_priority;
			errno = 0;
			d->proc_nice = getpriority(PRIO_PROCESS, 0);
		}
	}
	log_cb_time(d, t);

	if (d->mode && strcmp(d->mode, "stall") == 0 && !d->stall_at) {
		/* nothing */
	}
	if (d->mode && strcmp(d->mode, "stall") == 0 &&
	    d->stall_at > 0 && (int)d->cb_count == d->stall_at) {
		d->t_stall_start_ms = now_ms();
		usleep((useconds_t)d->stall_ms * 1000);
		d->t_stall_end_ms = now_ms();
	}

	if (d->mode && strcmp(d->mode, "drain") == 0 && d->nbuf > 0 &&
	    d->drain_at == 0 && d->cb_count >= 3 && d->flush_ms == 0) {
		d->flush_rc = pw_stream_flush(d->stream, true);
		d->flush_ms = now_ms();
	}

	b = pw_stream_dequeue_buffer(d->stream);
	if (b == NULL) {
		d->dequeue_null++;
		return;
	}
	buf = b->buffer;
	if (buf && buf->n_datas > 0 && buf->datas[0].data) {
		uint32_t sz = buf->datas[0].maxsize;
		void *p = buf->datas[0].data;
		if (d->direction == PW_DIRECTION_INPUT) {
			/* capture accounting on the actual chunk */
			uint32_t csz = buf->datas[0].chunk ? buf->datas[0].chunk->size : sz;
			uint32_t stride = buf->datas[0].chunk ? (uint32_t)buf->datas[0].chunk->stride : (uint32_t)(d->channels * 4);
			uint32_t i, ns;
			if (d->channels == 1 && !d->fmt_s16) {
				const float *x = p;
				ns = csz / 4;
				for (i = 0; i < ns; i++) {
					float v = x[i];
					double av = v < 0 ? -(double)v : (double)v;
					if (av > d->cap_peak) d->cap_peak = av;
					if (v != 0.0f) d->cap_nz++;
					d->cap_rms_sum += (double)v * (double)v;
					d->g997_re += v * d->g997_cr;
					d->g997_im += v * d->g997_ci;
					d->g440_re += v * d->g440_cr;
					d->g440_im += v * d->g440_ci;
					{
						double nc = d->g997_cr * d->g997_rot_c - d->g997_ci * d->g997_rot_s;
						double ni = d->g997_ci * d->g997_rot_c + d->g997_cr * d->g997_rot_s;
						d->g997_cr = nc; d->g997_ci = ni;
						nc = d->g440_cr * d->g440_rot_c - d->g440_ci * d->g440_rot_s;
						ni = d->g440_ci * d->g440_rot_c + d->g440_cr * d->g440_rot_s;
						d->g440_cr = nc; d->g440_ci = ni;
					}
					d->cap_sample_index++;
				}
				d->cap_frames += ns;
			} else if (d->channels == 1 && d->fmt_s16) {
				const int16_t *x = p;
				ns = csz / 2;
				for (i = 0; i < ns; i++) {
					double v = x[i] / 32768.0;
					double av = v < 0 ? -v : v;
					if (av > d->cap_peak) d->cap_peak = av;
					if (v != 0.0) d->cap_nz++;
					d->cap_rms_sum += v * v;
					d->cap_sample_index++;
				}
				d->cap_frames += ns;
			}
			(void)stride;
			/* recycle immediately for capture */
			pw_stream_queue_buffer(d->stream, b);
			return;
		}
		memset(p, 0, sz);
		if (buf->datas[0].chunk) {
			buf->datas[0].chunk->offset = 0;
			buf->datas[0].chunk->size = sz;
			buf->datas[0].chunk->stride = d->fmt_s16 ? (int32_t)(d->channels * 2) : (int32_t)(d->channels * 4);
		}
		d->cb_bytes += sz;
		d->last_maxsize = sz;
		if (buf->datas[0].chunk) {
			d->last_chunk_size = buf->datas[0].chunk->size;
			d->last_stride = (uint32_t)buf->datas[0].chunk->stride;
		}
		b->size = sz / (uint64_t)(d->channels * (d->fmt_s16 ? 2 : 4)); /* frames */
		d->last_bufid = (uint32_t)(b->requested & 0xffffffff);
	}
	d->last_nbufs = (uint32_t)b->size;
	if (pw_stream_queue_buffer(d->stream, b) < 0)
		d->queue_rc_err++;

	if (d->mode && strcmp(d->mode, "time") == 0 && d->cb_count == 8) {
		d->time_rc_after = pw_stream_get_time_n(d->stream, &d->ptime, sizeof(d->ptime));
		d->is_driving = pw_stream_is_driving(d->stream) ? 1 : 0;
		d->is_lazy = pw_stream_is_lazy(d->stream) ? 1 : 0;
		d->set_active2_rc = pw_stream_set_active(d->stream, false);
		d->set_rate_rc = pw_stream_set_rate(d->stream, 0.5);
		if (d->timer) {
			struct timespec v = { .tv_sec = 0, .tv_nsec = 150 * 1000 * 1000 };
			pw_loop_update_timer(pw_main_loop_get_loop(d->loop), d->timer, &v, NULL, false);
		}
	}
	if (d->mode && strcmp(d->mode, "run") == 0 && d->cb_count == 4) {
		d->time_rc_after = pw_stream_get_time_n(d->stream, &d->ptime, sizeof(d->ptime));
		d->is_driving = pw_stream_is_driving(d->stream) ? 1 : 0;
		d->is_lazy = pw_stream_is_lazy(d->stream) ? 1 : 0;
	}
}

static void on_drained(void *userdata)
{
	struct data *d = userdata;
	d->n_drained++;
	d->drained_flag = 1;
	if (d->n_drained == 1)
		d->first_drained_ms = now_ms();
	printf("EV drained t_ms=%llu\n", (unsigned long long)(now_ms() - d->t0_ms));
	fflush(stdout);
}

static void on_add_buffer(void *userdata, struct pw_buffer *b)
{
	struct data *d = userdata;
	d->n_add_buffer++;
	if (d->n_add_buffer == 1) {
		struct spa_buffer *buf = b->buffer;
		if (buf && buf->n_datas > 0)
			printf("EV add_buffer n_datas=%u maxsize=%u data=%s\n",
			       buf->n_datas, buf->datas[0].maxsize,
			       buf->datas[0].data ? "set" : "null");
		else
			printf("EV add_buffer n_datas=0\n");
		fflush(stdout);
	}
	if (d->flags & PW_STREAM_FLAG_ALLOC_BUFFERS) {
		struct spa_buffer *buf = b->buffer;
		if (buf && buf->n_datas > 0 && buf->datas[0].data == NULL) {
			d->add_buffer_data_null = 1;
			void *mem = calloc(1, buf->datas[0].maxsize);
			if (mem) {
				buf->datas[0].data = mem;
				if (buf->datas[0].chunk) {
					buf->datas[0].chunk->offset = 0;
					buf->datas[0].chunk->size = 0;
					buf->datas[0].chunk->stride = 4;
				}
				if (d->n_alloc_ptrs < 64)
					d->alloc_ptrs[d->n_alloc_ptrs++] = mem;
			}
		}
	}
}

static void on_remove_buffer(void *userdata, struct pw_buffer *b)
{
	struct data *d = userdata;
	(void)b;
	d->n_remove_buffer++;
	if (d->flags & PW_STREAM_FLAG_ALLOC_BUFFERS) {
		int i;
		for (i = 0; i < d->n_alloc_ptrs; i++) {
			free(d->alloc_ptrs[i]);
			d->alloc_ptrs[i] = NULL;
		}
		d->n_alloc_ptrs = 0;
	}
}

static void on_io_changed(void *userdata, uint32_t id, void *area, uint32_t size)
{
	struct data *d = userdata;
	(void)area; (void)size;
	d->n_io_changed++;
	printf("EV io_changed id=%u size=%u\n", id, size);
	fflush(stdout);
}

static void on_control_info(void *userdata, uint32_t id, const struct pw_stream_control *control)
{
	struct data *d = userdata;
	d->n_control_info++;
	printf("EV control_info id=%u name=%s n_values=%u\n", id,
	       control->name ? control->name : "-", control->n_values);
	fflush(stdout);
}

static void on_trigger_done(void *userdata)
{
	struct data *d = userdata;
	d->n_trigger_done++;
}

static const struct pw_stream_events stream_events = {
	PW_VERSION_STREAM_EVENTS,
	.state_changed = on_state_changed,
	.param_changed = on_param_changed,
	.process = on_process,
	.drained = on_drained,
	.add_buffer = on_add_buffer,
	.remove_buffer = on_remove_buffer,
	.io_changed = on_io_changed,
	.control_info = on_control_info,
	.trigger_done = on_trigger_done,
};

static void arm_timer(struct data *d, int ms);
static void arm_timer_rel(struct data *d, int ms);

static void on_timer(void *userdata, uint64_t expirations)
{
	struct data *d = userdata;
	uint64_t el;
	(void)expirations;
	el = now_ms() - d->t0_ms;
	if ((d->activate_after > 0 || d->trigger_after > 0 || d->drain_at > 0 ||
	     (d->mode && strcmp(d->mode, "drain") == 0)) && d->run_ms > 0 &&
	    el >= (uint64_t)(d->hold > 0 ? d->hold : d->run_ms)) {
		printf("EV timer_quit t_ms=%llu\n", (unsigned long long)el);
		fflush(stdout);
		pw_main_loop_quit(d->loop);
		return;
	}
	if (d->drain_at > 0 && !d->drain_done) {
		if (el >= (uint64_t)d->drain_at) {
			d->flush_rc = pw_stream_flush(d->stream, true);
			d->flush_ms = now_ms();
			d->drain_done = 1;
			printf("EV drain_flush rc=%d t_ms=%llu\n", d->flush_rc,
			       (unsigned long long)el);
			fflush(stdout);
		}
		arm_timer_rel(d, 20);
		return;
	}
	if (d->drain_done) {
		arm_timer_rel(d, 20);
		return;
	}
	if (d->activate_after > 0 && !d->activate_done) {
		if (el >= (uint64_t)d->activate_after) {
			d->set_active_rc = pw_stream_set_active(d->stream, true);
			d->activate_done = 1;
			printf("EV activate rc=%d t_ms=%llu\n", d->set_active_rc,
			       (unsigned long long)el);
			fflush(stdout);
		}
		arm_timer_rel(d, 20);
		return;
	}
	if (d->trigger_after > 0 && !d->trigger_done) {
		if (el >= (uint64_t)d->trigger_after) {
			d->trigger_done = 1;
			printf("EV trigger_start t_ms=%llu\n", (unsigned long long)el);
			fflush(stdout);
		}
		arm_timer_rel(d, 20);
		return;
	}
	if (d->trigger_done && d->trigger_count < 30) {
		d->trigger_rc = pw_stream_trigger_process(d->stream);
		d->trigger_count++;
		if (d->trigger_count <= 2)
			printf("EV trigger n=%d rc=%d cb=%llu t_ms=%llu\n",
			       d->trigger_count, d->trigger_rc,
			       (unsigned long long)d->cb_count,
			       (unsigned long long)el);
		fflush(stdout);
		arm_timer_rel(d, 40);
		return;
	}
	if (d->hold > 0 && el < (uint64_t)d->hold) {
		/* boundary-seat delta: keep observing (no early quit) */
		arm_timer_rel(d, 20);
		return;
	}
	printf("EV timer_quit t_ms=%llu\n", (unsigned long long)el);
	fflush(stdout);
	pw_main_loop_quit(d->loop);
}

static void arm_timer(struct data *d, int ms)
{
	if (!d->timer) {
		d->timer = pw_loop_add_timer(pw_main_loop_get_loop(d->loop), on_timer, d);
	}
	if (d->timer) {
		struct timespec v = { .tv_sec = ms / 1000, .tv_nsec = (long)(ms % 1000) * 1000000L };
		pw_loop_update_timer(pw_main_loop_get_loop(d->loop), d->timer, &v, NULL, false);
	}
}

static void arm_timer_rel(struct data *d, int ms)
{
	arm_timer(d, ms);
}

static enum pw_stream_flags parse_flags(const char *s)
{
	enum pw_stream_flags f = PW_STREAM_FLAG_NONE;
	char *copy = strdup(s);
	char *tok, *save = NULL;
	for (tok = strtok_r(copy, ",", &save); tok; tok = strtok_r(NULL, ",", &save)) {
		if (!strcmp(tok, "autoconnect")) f |= PW_STREAM_FLAG_AUTOCONNECT;
		else if (!strcmp(tok, "inactive")) f |= PW_STREAM_FLAG_INACTIVE;
		else if (!strcmp(tok, "map_buffers")) f |= PW_STREAM_FLAG_MAP_BUFFERS;
		else if (!strcmp(tok, "driver")) f |= PW_STREAM_FLAG_DRIVER;
		else if (!strcmp(tok, "rt_process")) f |= PW_STREAM_FLAG_RT_PROCESS;
		else if (!strcmp(tok, "no_convert")) f |= PW_STREAM_FLAG_NO_CONVERT;
		else if (!strcmp(tok, "exclusive")) f |= PW_STREAM_FLAG_EXCLUSIVE;
		else if (!strcmp(tok, "dont_reconnect")) f |= PW_STREAM_FLAG_DONT_RECONNECT;
		else if (!strcmp(tok, "alloc_buffers")) f |= PW_STREAM_FLAG_ALLOC_BUFFERS;
		else if (!strcmp(tok, "trigger")) f |= PW_STREAM_FLAG_TRIGGER;
		else if (!strcmp(tok, "async")) f |= PW_STREAM_FLAG_ASYNC;
		else if (!strcmp(tok, "early_process")) f |= PW_STREAM_FLAG_EARLY_PROCESS;
		else if (!strcmp(tok, "rt_trigger_done")) f |= PW_STREAM_FLAG_RT_TRIGGER_DONE;
		else { fprintf(stderr, "unknown flag %s\n", tok); exit(2); }
	}
	free(copy);
	return f;
}

static void apply_props(struct pw_properties *p, const char *kv)
{
	char *copy = strdup(kv);
	char *tok, *save = NULL;
	for (tok = strtok_r(copy, ";", &save); tok; tok = strtok_r(NULL, ";", &save)) {
		char *eq = strchr(tok, '=');
		if (!eq) continue;
		*eq = 0;
		pw_properties_set(p, tok, eq + 1);
	}
	free(copy);
}

static void print_props(struct data *d, const char *tag)
{
	const struct pw_properties *p = pw_stream_get_properties(d->stream);
	const struct spa_dict_item *it;
	spa_dict_for_each(it, &p->dict) {
		printf("PROP %s %s=%s\n", tag, it->key, it->value);
	}
	fflush(stdout);
}

static void make_params(struct data *d, uint8_t *buf, size_t bufsz,
			const struct spa_pod **params, uint32_t *n_params,
			struct spa_pod_builder *b_out)
{
	struct spa_pod_builder b = SPA_POD_BUILDER_INIT(buf, bufsz);
	struct spa_audio_info_raw info;
	memset(&info, 0, sizeof(info));
	info.format = d->fmt_s16 ? SPA_AUDIO_FORMAT_S16 : SPA_AUDIO_FORMAT_F32;
	info.rate = (uint32_t)d->rate;
	info.channels = (uint32_t)d->channels;
	if (d->channels == 1) {
		info.position[0] = SPA_AUDIO_CHANNEL_MONO;
	} else {
		info.position[0] = SPA_AUDIO_CHANNEL_FL;
		info.position[1] = SPA_AUDIO_CHANNEL_FR;
	}
	params[0] = spa_format_audio_raw_build(&b, SPA_PARAM_EnumFormat, &info);
	*n_params = 1;
	*b_out = b;
}

int main(int argc, char *argv[])
{
	struct data d;
	struct pw_properties *props;
	uint8_t podbuf[1024];
	const struct spa_pod *params[1];
	struct spa_pod_builder b;
	uint32_t n_params = 0;
	int i;

	memset(&d, 0, sizeof(d));
	d.rate = 48000;
	d.channels = 1;
	d.run_ms = 1500;
	d.nbuf = 5;
	d.direction = PW_DIRECTION_OUTPUT;

	if (argc < 2) {
		fprintf(stderr, "usage: %s <mode> [key=value ...]\n", argv[0]);
		return 2;
	}
	d.mode = argv[1];
	for (i = 2; i < argc; i++) {
		char *eq = strchr(argv[i], '=');
		if (!eq) continue;
		*eq = 0;
		const char *k = argv[i], *v = eq + 1;
		if (!strcmp(k, "target")) d.target = (char *)v;
		else if (!strcmp(k, "props")) d.extra_props = (char *)v;
		else if (!strcmp(k, "flags")) d.flag_str = (char *)v;
		else if (!strcmp(k, "ms")) d.run_ms = atoi(v);
		else if (!strcmp(k, "stall_at")) d.stall_at = atoi(v);
		else if (!strcmp(k, "stall_ms")) d.stall_ms = atoi(v);
		else if (!strcmp(k, "nbuf")) d.nbuf = atoi(v);
		else if (!strcmp(k, "rate")) d.rate = atoi(v);
		else if (!strcmp(k, "channels")) d.channels = atoi(v);
		else if (!strcmp(k, "fmt")) d.fmt_s16 = !strcmp(v, "s16");
		else if (!strcmp(k, "dir")) d.direction = !strcmp(v, "in") ? PW_DIRECTION_INPUT : PW_DIRECTION_OUTPUT;
		else if (!strcmp(k, "no_params")) d.no_params = atoi(v);
		else if (!strcmp(k, "activate_after")) d.activate_after = atoi(v);
		else if (!strcmp(k, "trigger_after")) d.trigger_after = atoi(v);
		else if (!strcmp(k, "drain_at")) d.drain_at = atoi(v);
		else if (!strcmp(k, "case")) d.err_case = (char *)v;
		else if (!strcmp(k, "hold")) d.hold = atoi(v);
		else if (!strcmp(k, "name")) d.name = (char *)v;
	}
	if (d.flag_str) d.flags = parse_flags(d.flag_str);
	d.arm_ms = d.run_ms;
	if (d.activate_after > 0 && d.activate_after < d.arm_ms) d.arm_ms = d.activate_after;
	if (d.trigger_after > 0 && d.trigger_after < d.arm_ms) d.arm_ms = d.trigger_after;
	if (d.drain_at > 0 && d.drain_at < d.arm_ms) d.arm_ms = d.drain_at;

	d.t0_ms = now_ms();
	d.main_tid = (int)syscall(SYS_gettid);
	d.main_sched = sched_getscheduler(0);
	{
		struct sched_param sp;
		if (sched_getparam(0, &sp) == 0)
			d.main_prio = sp.sched_priority;
	}

	pw_init(&argc, &argv);
	{
		double w997 = 2.0 * M_PI * 997.0 / (double)d.rate;
		double w440 = 2.0 * M_PI * 440.0 / (double)d.rate;
		d.g997_rot_c = cos(w997); d.g997_rot_s = sin(w997);
		d.g440_rot_c = cos(w440); d.g440_rot_s = sin(w440);
		d.g997_cr = 1.0; d.g997_ci = 0.0;
		d.g440_cr = 1.0; d.g440_ci = 0.0;
	}
	printf("R98 mode=%s\n", d.mode);
	printf("R98 library_version=%s\n", pw_get_library_version());
	fflush(stdout);

	d.loop = pw_main_loop_new(NULL);
	d.context = pw_context_new(pw_main_loop_get_loop(d.loop), NULL, 0);
	d.core = pw_context_connect(d.context, NULL, 0);
	if (d.core == NULL) {
		printf("R98 connect_rc=%d errno=%d\n", -errno, errno);
		return 1;
	}
	pw_core_add_listener(d.core, &d.core_listener, &core_events, &d);

	if (!strcmp(d.mode, "info")) {
		arm_timer(&d, 600);
		pw_main_loop_run(d.loop);
		if (d.core_info) {
			printf("R98 core_name=%s\n", d.core_info->name ? d.core_info->name : "-");
			printf("R98 core_version=%s\n", d.core_info->version ? d.core_info->version : "-");
			printf("R98 core_user=%s\n", d.core_info->user_name ? d.core_info->user_name : "-");
			printf("R98 core_host=%s\n", d.core_info->host_name ? d.core_info->host_name : "-");
			printf("R98 core_cookie=%u\n", d.core_info->cookie);
			if (d.core_info->props) {
				const struct spa_dict_item *it;
				spa_dict_for_each(it, d.core_info->props)
					printf("R98 core_prop %s=%s\n", it->key, it->value);
			}
		} else {
			printf("R98 core_info=absent\n");
		}
		printf("R98 connect_rc=0\n");
		goto done;
	}

	{
		char namebuf[64];
		snprintf(namebuf, sizeof(namebuf), "r98b_%s", d.name ? d.name : d.mode);
		props = pw_properties_new(
			PW_KEY_NODE_NAME, namebuf,
			PW_KEY_MEDIA_TYPE, "Audio",
			PW_KEY_MEDIA_CATEGORY, d.direction == PW_DIRECTION_OUTPUT ? "Playback" : "Capture",
			PW_KEY_MEDIA_ROLE, "DSP",
			PW_KEY_APP_NAME, "r98bstream",
			"state.restore-props", "false",
			NULL);
		if (d.direction == PW_DIRECTION_OUTPUT)
			pw_properties_set(props, PW_KEY_MEDIA_CLASS, "Stream/Output/Audio");
		else
			pw_properties_set(props, PW_KEY_MEDIA_CLASS, "Stream/Input/Audio");
		if (d.target)
			pw_properties_set(props, PW_KEY_TARGET_OBJECT, d.target);
		if (d.extra_props)
			apply_props(props, d.extra_props);
		d.stream = pw_stream_new(d.core, namebuf, props);
		pw_stream_add_listener(d.stream, &d.stream_listener, &stream_events, &d);
	}

	if (!strcmp(d.mode, "error")) {
		const char *c = d.err_case ? d.err_case : "";
		if (!strcmp(c, "set_active_pre")) {
			d.set_active_rc = pw_stream_set_active(d.stream, true);
			printf("R98 set_active_pre_rc=%d\n", d.set_active_rc);
			d.time_rc_before = pw_stream_get_time_n(d.stream, &d.ptime, sizeof(d.ptime));
			printf("R98 get_time_pre_rc=%d\n", d.time_rc_before);
			d.disconnect_rc = pw_stream_disconnect(d.stream);
			printf("R98 disconnect_pre_rc=%d\n", d.disconnect_rc);
			d.flush_rc = pw_stream_flush(d.stream, true);
			printf("R98 flush_pre_rc=%d\n", d.flush_rc);
			d.set_rate_rc = pw_stream_set_rate(d.stream, 0.5);
			printf("R98 set_rate_pre_rc=%d\n", d.set_rate_rc);
			goto done;
		}
		if (!strcmp(c, "bad_direction")) {
			d.connect_rc = pw_stream_connect(d.stream, (enum pw_direction)99, PW_ID_ANY,
							 d.flags, NULL, 0);
			printf("R98 connect_rc=%d\n", d.connect_rc);
			goto done;
		}
		if (!strcmp(c, "connect_twice")) {
			make_params(&d, podbuf, sizeof(podbuf), params, &n_params, &b);
			d.connect_rc = pw_stream_connect(d.stream, d.direction, PW_ID_ANY,
							 PW_STREAM_FLAG_INACTIVE, params, n_params);
			printf("R98 connect_rc=%d\n", d.connect_rc);
			{
				int rc2 = pw_stream_connect(d.stream, d.direction, PW_ID_ANY,
							    PW_STREAM_FLAG_INACTIVE, params, n_params);
				printf("R98 connect2_rc=%d\n", rc2);
			}
			arm_timer(&d, 300);
			pw_main_loop_run(d.loop);
			goto done;
		}
		if (!strcmp(c, "no_params")) {
			d.connect_rc = pw_stream_connect(d.stream, d.direction, PW_ID_ANY,
							 d.flags | PW_STREAM_FLAG_INACTIVE, NULL, 0);
			printf("R98 connect_rc=%d\n", d.connect_rc);
			arm_timer(&d, 300);
			pw_main_loop_run(d.loop);
			printf("R98 state=%s\n", state_str(d.state));
			goto done;
		}
		if (!strcmp(c, "queue_unowned")) {
			struct pw_buffer *b0 = pw_stream_dequeue_buffer(d.stream);
			printf("R98 dequeue_pre_rc=%p\n", (void *)b0);
			if (b0) {
				int rc = pw_stream_queue_buffer(d.stream, b0);
				printf("R98 queue_pre_rc=%d\n", rc);
			}
			d.disconnect_rc = pw_stream_disconnect(d.stream);
			printf("R98 disconnect_pre_rc=%d\n", d.disconnect_rc);
			goto done;
		}
		fprintf(stderr, "unknown error case '%s'\n", c);
		goto done;
	}

	if (d.no_params) {
		d.connect_rc = pw_stream_connect(d.stream, d.direction, PW_ID_ANY,
						 d.flags | PW_STREAM_FLAG_INACTIVE, NULL, 0);
	} else {
		make_params(&d, podbuf, sizeof(podbuf), params, &n_params, &b);
		d.connect_rc = pw_stream_connect(d.stream, d.direction, PW_ID_ANY,
						 d.flags, params, n_params);
	}
	d.t_connect_ms = now_ms();
	d.node_id = pw_stream_get_node_id(d.stream);
	printf("R98 connect_rc=%d\n", d.connect_rc);
	printf("R98 node_id=%u\n", d.node_id);
	printf("R98 flags=%u\n", (unsigned)d.flags);
	fflush(stdout);

	if (!strcmp(d.mode, "state")) {
		d.time_rc_before = pw_stream_get_time_n(d.stream, &d.ptime, sizeof(d.ptime));
		printf("R98 get_time_pre_rc=%d\n", d.time_rc_before);
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 1200);
		pw_main_loop_run(d.loop);
		printf("R98 node_id_final=%u\n", pw_stream_get_node_id(d.stream));
		d.is_driving = pw_stream_is_driving(d.stream) ? 1 : 0;
		d.is_lazy = pw_stream_is_lazy(d.stream) ? 1 : 0;
		print_props(&d, "after");
		d.disconnect_rc = pw_stream_disconnect(d.stream);
		printf("R98 disconnect_rc=%d\n", d.disconnect_rc);
		goto done;
	}

	if (!strcmp(d.mode, "time")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 1500);
		pw_main_loop_run(d.loop);
		/* second get_time after deactivation */
		d.time_rc_before = pw_stream_get_time_n(d.stream, &d.ptime, sizeof(d.ptime));
		printf("R98 get_time_after_deactivate_rc=%d\n", d.time_rc_before);
		printf("R98 set_active_false_rc=%d\n", d.set_active2_rc);
		goto finish;
	}

	if (!strcmp(d.mode, "drain")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 2500);
		pw_main_loop_run(d.loop);
		printf("R98 flush_rc=%d\n", d.flush_rc);
		goto finish;
	}

	if (!strcmp(d.mode, "neg")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 900);
		pw_main_loop_run(d.loop);
		/* mid-stream update: new rate */
		{
			uint8_t podbuf2[1024];
			struct spa_pod_builder b2 = SPA_POD_BUILDER_INIT(podbuf2, sizeof(podbuf2));
			struct spa_audio_info_raw info;
			const struct spa_pod *p2[1];
			memset(&info, 0, sizeof(info));
			info.format = d.fmt_s16 ? SPA_AUDIO_FORMAT_S16 : SPA_AUDIO_FORMAT_F32;
			info.rate = 44100;
			info.channels = (uint32_t)d.channels;
			if (d.channels == 1) info.position[0] = SPA_AUDIO_CHANNEL_MONO;
			else { info.position[0] = SPA_AUDIO_CHANNEL_FL; info.position[1] = SPA_AUDIO_CHANNEL_FR; }
			p2[0] = spa_format_audio_raw_build(&b2, SPA_PARAM_EnumFormat, &info);
			d.update_params_rc = pw_stream_update_params(d.stream, p2, 1);
			printf("R98 update_params_rc=%d\n", d.update_params_rc);
		}
		d.n_params_seen = 0;
		d.n_param_changed = 0;
		d.fmt_rate = 0;
		arm_timer(&d, 700);
		pw_main_loop_run(d.loop);
		goto finish;
	}

	if (!strcmp(d.mode, "cap")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 1200);
		pw_main_loop_run(d.loop);
		goto finish;
	}

	if (!strcmp(d.mode, "flags")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 1200);
		pw_main_loop_run(d.loop);
		print_props(&d, "after");
		goto finish;
	}

	if (!strcmp(d.mode, "props")) {
		arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : 900);
		pw_main_loop_run(d.loop);
		print_props(&d, "after");
		goto finish;
	}

	/* run / stall */
	arm_timer(&d, d.arm_ms > 0 ? d.arm_ms : d.run_ms);
	pw_main_loop_run(d.loop);

finish:
	d.is_driving = pw_stream_is_driving(d.stream) ? 1 : 0;
	d.is_lazy = pw_stream_is_lazy(d.stream) ? 1 : 0;
	printf("R98 node_id_final=%u\n", pw_stream_get_node_id(d.stream));
	printf("R98 state=%s\n", state_str(d.state));
	printf("R98 stream_error=%s\n", d.stream_error_seen ? d.error_str : "-");
	printf("R98 cb_count=%llu\n", (unsigned long long)d.cb_count);
	printf("R98 cb_bytes=%llu\n", (unsigned long long)d.cb_bytes);
	printf("R98 dequeue_null=%d\n", d.dequeue_null);
	printf("R98 queue_err=%d\n", d.queue_rc_err);
	printf("R98 last_maxsize=%u\n", d.last_maxsize);
	printf("R98 last_chunk_size=%u\n", d.last_chunk_size);
	printf("R98 last_stride=%u\n", d.last_stride);
	printf("R98 last_bufid=%u\n", d.last_bufid);
	printf("R98 last_nbufs=%u\n", d.last_nbufs);
	printf("R98 n_add_buffer=%d\n", d.n_add_buffer);
	printf("R98 n_remove_buffer=%d\n", d.n_remove_buffer);
	printf("R98 n_drained=%d first_drained_ms=%llu\n", d.n_drained,
	       (unsigned long long)(d.first_drained_ms ? d.first_drained_ms - d.t0_ms : 0));
	printf("R98 n_trigger_done=%d\n", d.n_trigger_done);
	printf("R98 n_io_changed=%d\n", d.n_io_changed);
	printf("R98 n_control_info=%d\n", d.n_control_info);
	printf("R98 n_param_changed=%d\n", d.n_param_changed);
	printf("R98 param_ids=");
	for (i = 0; i < d.n_params_seen; i++)
		printf("%s%d", i ? "," : "", d.param_ids[i]);
	printf("\n");
	printf("R98 fmt_seen=%d fmt_format=%u fmt_rate=%u fmt_channels=%u\n",
	       d.fmt_seen, d.fmt_format, d.fmt_rate, d.fmt_channels);
	printf("R98 t_first_cb_ms=%llu t_streaming_ms=%llu t_connect_ms=%llu t_end_ms=%llu\n",
	       (unsigned long long)(d.t_first_cb_ms ? d.t_first_cb_ms - d.t0_ms : 0),
	       (unsigned long long)(d.t_streaming_ms ? d.t_streaming_ms - d.t0_ms : 0),
	       (unsigned long long)(d.t_connect_ms - d.t0_ms),
	       (unsigned long long)(now_ms() - d.t0_ms));
	printf("R98 stall_start_ms=%llu stall_end_ms=%llu stall_gap_ms=%llu\n",
	       (unsigned long long)(d.t_stall_start_ms ? d.t_stall_start_ms - d.t0_ms : 0),
	       (unsigned long long)(d.t_stall_end_ms ? d.t_stall_end_ms - d.t0_ms : 0),
	       (unsigned long long)(d.t_stall_end_ms - d.t_stall_start_ms));
	printf("R98 proc_tid=%d proc_sched=%d proc_prio=%d proc_nice=%d main_tid=%d main_sched=%d main_prio=%d\n",
	       d.proc_tid, d.proc_sched, d.proc_prio, d.proc_nice, d.main_tid, d.main_sched, d.main_prio);
	printf("R98 time_rc_after=%d now=%llu rate_num=%u rate_denom=%u ticks=%llu delay=%lld queued=%llu buffered=%llu queued_buffers=%u avail_buffers=%u size=%llu\n",
	       d.time_rc_after, (unsigned long long)d.ptime.now,
	       d.ptime.rate.num, d.ptime.rate.denom,
	       (unsigned long long)d.ptime.ticks, (long long)d.ptime.delay,
	       (unsigned long long)d.ptime.queued, (unsigned long long)d.ptime.buffered,
	       d.ptime.queued_buffers, d.ptime.avail_buffers,
	       (unsigned long long)d.ptime.size);
	printf("R98 is_driving=%d is_lazy=%d\n", d.is_driving, d.is_lazy);
	printf("R98 add_buffer_data_null=%d\n", d.add_buffer_data_null);
	printf("R98 cap_frames=%llu cap_nz=%llu cap_peak=%.6f cap_rms=%.6f g997_mag2=%.3f g440_mag2=%.3f\n",
	       (unsigned long long)d.cap_frames, (unsigned long long)d.cap_nz,
	       d.cap_peak,
	       d.cap_frames ? sqrt(d.cap_rms_sum / (double)d.cap_frames) : 0.0,
	       d.g997_re * d.g997_re + d.g997_im * d.g997_im,
	       d.g440_re * d.g440_re + d.g440_im * d.g440_im);
	printf("R98 set_active_rc=%d activate_done=%d trigger_done=%d trigger_count=%d trigger_rc=%d set_rate_rc=%d\n",
	       d.set_active_rc, d.activate_done, d.trigger_done, d.trigger_count, d.trigger_rc, d.set_rate_rc);
	printf("R98 cb_log=");
	for (i = 0; i < d.cb_log_n; i++)
		printf("%s%llu", i ? "," : "", (unsigned long long)(d.cb_log[i] - d.t0_ms));
	printf("\n");
	fflush(stdout);

done:
	if (d.stream) {
		pw_stream_destroy(d.stream);
	}
	pw_core_disconnect(d.core);
	pw_context_destroy(d.context);
	pw_main_loop_destroy(d.loop);
	pw_deinit();
	printf("R98 exit=0\n");
	return 0;
}
