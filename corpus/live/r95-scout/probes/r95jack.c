/* r95 scout — JACK<->PipeWire interop probe client.
 *
 * Seat-owned names only (r95s_*). One JSON line per mode on stdout prefixed
 * "R95JSON ". Built against the host's only libjack (pipewire-jack 1.6.8).
 * No daemon config is touched; every link is made to seat-owned objects.
 *
 * modes: info shape tone stall bufsize latency transport metadata xconnect
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <math.h>
#include <jack/jack.h>
#include <jack/statistics.h>
#include <jack/metadata.h>
#include <jack/uuid.h>

static volatile sig_atomic_t g_stop = 0;
static void on_sig(int s) { (void)s; g_stop = 1; }

/* present in pipewire-jack's libjack but absent from the installed headers */
extern char *jack_client_get_uuid(jack_client_t *client);
extern int jack_client_real_time_priority(jack_client_t *client);
extern int jack_client_max_real_time_priority(jack_client_t *client);

#define MAXL 256

struct counters {
	unsigned long cb, cb_in_nonzero, in_samples, in_nonzero;
	double in_sum, in_sumsq, in_peak, in_rms;
	double g1, g2;              /* Goertzel state */
	double g_coef;              /* 2*cos(2*pi*f/fs) */
	unsigned long xruns, bufsize_cbs, srate_cbs, reg_cbs, conn_cbs, graph_cbs, fw_cbs;
	unsigned long last_bufsize, last_srate;
	jack_nframes_t first_lft, last_lft;
	unsigned long stall_cycles;
	double stall_us;
};

static struct counters C;
static jack_client_t *g_client;
static jack_port_t *p_out, *p_in, *p_outp, *p_outt, *p_outm;
static double g_phase, g_dphase;
static double g_amp = 0.5;
static unsigned long g_stall_every, g_stall_us;
static int g_in_analysis = 1;

static int process_cb(jack_nframes_t nframes, void *arg)
{
	(void)arg;
	C.cb++;
	if (C.first_lft == 0)
		C.first_lft = jack_last_frame_time(g_client);
	C.last_lft = jack_last_frame_time(g_client);
	if (g_stall_every && (C.cb % g_stall_every) == 0) {
		usleep(g_stall_us);
		C.stall_cycles++;
	}
	if (p_out != NULL) {
		float *o = (float *)jack_port_get_buffer(p_out, nframes);
		if (o != NULL) {
			for (jack_nframes_t i = 0; i < nframes; i++) {
				o[i] = (float)(g_amp * sin(g_phase));
				g_phase += g_dphase;
				if (g_phase > 2.0 * M_PI) g_phase -= 2.0 * M_PI;
			}
		}
	}
	if (p_in != NULL && g_in_analysis) {
		float *ib = (float *)jack_port_get_buffer(p_in, nframes);
		if (ib != NULL) {
			unsigned long nz = 0;
			for (jack_nframes_t i = 0; i < nframes; i++) {
				double x = ib[i];
				C.in_sum += x; C.in_sumsq += x * x; C.in_samples++;
				if (fabs(x) > 1e-6) nz++;
				if (fabs(x) > C.in_peak) C.in_peak = fabs(x);
				double s = x + C.g_coef * C.g1 - C.g2;
				C.g2 = C.g1; C.g1 = s;
			}
			C.in_nonzero += nz;
			if (nz > 0) C.cb_in_nonzero++;
		}
	}
	return 0;
}

static int xrun_cb(void *arg) { (void)arg; C.xruns++; return 0; }
static int bufsize_cb(jack_nframes_t n, void *arg) { (void)arg; C.bufsize_cbs++; C.last_bufsize = n; return 0; }
static int srate_cb(jack_nframes_t n, void *arg) { (void)arg; C.srate_cbs++; C.last_srate = n; return 0; }
static void reg_cb(jack_port_id_t a, int b, void *arg) { (void)a;(void)b;(void)arg; C.reg_cbs++; }
static void conn_cb(jack_port_id_t a, jack_port_id_t b, int c, void *arg) { (void)a;(void)b;(void)c;(void)arg; C.conn_cbs++; }
static int graph_cb(void *arg) { (void)arg; C.graph_cbs++; return 0; }
static void fw_cb(int a, void *arg) { (void)a;(void)arg; C.fw_cbs++; }

static void jstr(const char *s)
{
	/* minimal JSON string escape */
	putchar('"');
	for (; s && *s; s++) {
		if (*s == '"' || *s == '\\') { putchar('\\'); putchar(*s); }
		else if ((unsigned char)*s < 0x20) printf("\\u%04x", *s);
		else putchar(*s);
	}
	putchar('"');
}

static jack_client_t *open_client(const char *name, jack_status_t *status)
{
	jack_options_t opt = (jack_options_t)(JackNoStartServer | JackUseExactName);
	jack_status_t st;
	jack_client_t *c = jack_client_open(name, opt, &st, NULL);
	if (status) *status = st;
	if (c == NULL) {
		printf("R95JSON {\"mode\":\"open\",\"ok\":false,\"status\":%d}\n", (int)st);
		fflush(stdout);
		exit(3);
	}
	return c;
}

static void print_common(jack_client_t *c)
{
	int maj, min, mic, proto;
	char uuidbuf[64];
	char *us = jack_client_get_uuid(c);
	jack_uuid_t u = 0;
	if (us) { jack_uuid_parse(us, &u); snprintf(uuidbuf, sizeof(uuidbuf), "%s", us); jack_free(us); }
	jack_get_version(&maj, &min, &mic, &proto);
	jack_uuid_unparse(u, uuidbuf);
	printf("\"version\":\"%s\",\"version_ints\":[%d,%d,%d,%d],"
	       "\"client_name\":", jack_get_version_string(), maj, min, mic, proto);
	jstr(jack_get_client_name(c));
	printf(",\"client_uuid\":\"%s\",\"client_pid\":%d,"
	       "\"client_name_size\":%d,\"port_name_size\":%d,"
	       "\"is_realtime\":%d,\"rt_prio\":%d,\"max_rt_prio\":%d,"
	       "\"cpu_load\":%.6f,\"jack_time_us\":%llu",
	       uuidbuf, jack_get_client_pid(jack_get_client_name(c)),
	       jack_client_name_size(), jack_port_name_size(),
	       jack_is_realtime(c), jack_client_real_time_priority(c),
	       jack_client_max_real_time_priority(c), jack_cpu_load(c),
	       (unsigned long long)jack_get_time());
}

static void print_counters(void)
{
	double gmag2 = C.g1 * C.g1 + C.g2 * C.g2 - C.g_coef * C.g1 * C.g2;
	printf("\"cb\":%lu,\"cb_in_nonzero\":%lu,\"in_samples\":%lu,\"in_nonzero\":%lu,"
	       "\"in_sum\":%.6f,\"in_rms\":%.9f,\"in_peak\":%.9f,\"goertzel_mag2\":%.9f,"
	       "\"xrun_cbs\":%lu,\"stall_cycles\":%lu,"
	       "\"bufsize_cbs\":%lu,\"last_bufsize\":%lu,"
	       "\"srate_cbs\":%lu,\"last_srate\":%lu,"
	       "\"reg_cbs\":%lu,\"conn_cbs\":%lu,\"graph_cbs\":%lu,\"fw_cbs\":%lu,"
	       "\"first_last_frame\":%u,\"last_last_frame\":%u",
	       C.cb, C.cb_in_nonzero, C.in_samples, C.in_nonzero,
	       C.in_sum, C.in_samples ? sqrt(C.in_sumsq / (double)C.in_samples) : 0.0,
	       C.in_peak, gmag2,
	       C.xruns, C.stall_cycles,
	       C.bufsize_cbs, C.last_bufsize, C.srate_cbs, C.last_srate,
	       C.reg_cbs, C.conn_cbs, C.graph_cbs, C.fw_cbs,
	       C.first_lft, C.last_lft);
}

static void print_cycle_times(jack_client_t *c)
{
	jack_nframes_t cf = 0;
	jack_time_t cu = 0, nu = 0;
	float pu = 0;
	int r = jack_get_cycle_times(c, &cf, &cu, &nu, &pu);
	printf(",\"cycle_times_rc\":%d,\"cycle_frames\":%u,\"cycle_usecs\":%llu,"
	       "\"cycle_next_usecs\":%llu,\"cycle_period_usecs\":%.3f",
	       r, cf, (unsigned long long)cu, (unsigned long long)nu, pu);
}

static void print_latency(jack_port_t *p, const char *label)
{
	jack_latency_range_t cap = {0, 0}, play = {0, 0};
	if (p == NULL) { printf(",\"%s\":null", label); return; }
	jack_port_get_latency_range(p, JackCaptureLatency, &cap);
	jack_port_get_latency_range(p, JackPlaybackLatency, &play);
	printf(",\"%s\":{\"name\":", label);
	jstr(jack_port_name(p));
	printf(",\"short\":");
	jstr(jack_port_short_name(p));
	printf(",\"flags\":%lu,\"type\":", (unsigned long)jack_port_flags(p));
	jstr(jack_port_type(p));
	printf(",\"lat_cap\":[%u,%u],\"lat_play\":[%u,%u],\"total\":%u",
	       cap.min, cap.max, play.min, play.max, jack_port_get_total_latency(g_client, p));
	{
		char *al[2] = {NULL, NULL};
		int na = jack_port_get_aliases(p, al);
		printf(",\"aliases\":[");
		for (int i = 0; i < na && i < 2; i++) {
			if (i) putchar(',');
			jstr(al[i]);
		}
		printf("]");
	}
	printf("}");
}

static double mono_us(void)
{
	struct timespec ts;
	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec * 1e6 + ts.tv_nsec / 1e3;
}

int main(int argc, char **argv)
{
	const char *mode = argc > 1 ? argv[1] : "info";
	double dur = argc > 2 ? atof(argv[2]) : 1.0;
	jack_status_t status = 0;

	signal(SIGTERM, on_sig);
	signal(SIGINT, on_sig);

	if (!strcmp(mode, "info")) {
		jack_client_t *c = open_client("r95s_info", &status);
		double t0 = mono_us();
		jack_time_t j0 = jack_get_time();
		printf("R95JSON {\"mode\":\"info\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"srate_inactive\":%u,\"bufsize_inactive\":%u,"
		       "\"srate\":%u,\"bufsize\":%u,", jack_get_sample_rate(c),
		       jack_get_buffer_size(c), jack_get_sample_rate(c), jack_get_buffer_size(c));
		jack_activate(c);
		printf("\"srate_active\":%u,\"bufsize_active\":%u,"
		       "\"is_realtime_active\":%d,\"cpu_load_active\":%.6f",
		       jack_get_sample_rate(c), jack_get_buffer_size(c),
		       jack_is_realtime(c), jack_cpu_load(c));
		print_cycle_times(c);
		/* wait for the graph to run (if it does) */
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		printf(",\"srate_live\":%u,\"bufsize_live\":%u,"
		       "\"is_realtime_live\":%d,\"cpu_load_live\":%.6f",
		       jack_get_sample_rate(c), jack_get_buffer_size(c),
		       jack_is_realtime(c), jack_cpu_load(c));
		print_cycle_times(c);
		printf(",\"jack_time_delta_us\":%lld,\"mono_delta_us\":%.1f,"
		       "\"frame_time\":%u,\"last_frame_time\":%u,"
		       "\"frames_since_cycle_start\":%u,"
		       "\"frames_to_time\":%llu,\"time_to_frames\":%u",
		       (long long)(jack_get_time() - j0), mono_us() - t0,
		       jack_frame_time(c), jack_last_frame_time(c),
		       jack_frames_since_cycle_start(c),
		       (unsigned long long)jack_frames_to_time(c, jack_frame_time(c)),
		       jack_time_to_frames(c, jack_get_time()));
		printf(",\"client_name_by_uuid\":");
		char ub[64]; char *us2 = jack_client_get_uuid(c);
		jack_uuid_t u = 0;
		if (us2) { jack_uuid_parse(us2, &u); jack_uuid_unparse(u, ub); }
		jstr(jack_get_client_name_by_uuid(c, ub));
		if (us2) jack_free(us2);
		printf(",\"uuid_for_name\":");
		char *uu = jack_get_uuid_for_client_name(c, jack_get_client_name(c));
		jstr(uu);
		if (uu) jack_free(uu);
		printf("}\n");
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "shape")) {
		jack_client_t *c = open_client("r95s_shape", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		p_in = jack_port_register(c, "in", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
		p_outp = jack_port_register(c, "outp", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput | JackPortIsPhysical, 0);
		p_outt = jack_port_register(c, "outt", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput | JackPortIsTerminal, 0);
		p_outm = jack_port_register(c, "outm", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput | JackPortCanMonitor, 0);
		jack_activate(c);
		/* optional early cross-domain connect: my out -> argv[3] (held through the run) */
		int xc_done = 0, xc_found = 0, xc_rc = -999, xc_conns_n = 0;
		char xc_dst[512] = "";
		char xc_conns[4][512];
		if (argc > 3) {
			snprintf(xc_dst, sizeof(xc_dst), "%s", argv[3]);
			jack_port_t *dp = jack_port_by_name(c, argv[3]);
			xc_found = dp != NULL;
			xc_rc = jack_connect(c, jack_port_name(p_out), argv[3]);
			{
				const char **cn = jack_port_get_connections(p_out);
				if (cn) {
					for (int k = 0; cn[k] && k < 4; k++)
						snprintf(xc_conns[xc_conns_n++], sizeof(xc_conns[0]), "%s", cn[k]);
					jack_free(cn);
				}
			}
			xc_done = 1;
		}
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);

		printf("R95JSON {\"mode\":\"shape\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"ports\":{\"out\":");
		{
			const char *n = p_out ? jack_port_name(p_out) : NULL;
			jstr(n);
			printf(",\"in\":");
			jstr(p_in ? jack_port_name(p_in) : NULL);
			printf(",\"outp\":");
			jstr(p_outp ? jack_port_name(p_outp) : NULL);
			printf(",\"outt\":");
			jstr(p_outt ? jack_port_name(p_outt) : NULL);
			printf(",\"outm\":");
			jstr(p_outm ? jack_port_name(p_outm) : NULL);
			printf("}");
		}
		print_latency(p_out, "lat_out");
		print_latency(p_in, "lat_in");
		print_latency(p_outp, "lat_outp");
		print_latency(p_outt, "lat_outt");
		print_latency(p_outm, "lat_outm");

		/* monitor API on the CanMonitor port */
		if (p_outm != NULL) {
			printf(",\"request_monitor_rc\":%d,\"monitoring_input\":%d,"
			       "\"ensure_monitor_rc\":%d",
			       jack_port_request_monitor(p_outm, 1),
			       jack_port_monitoring_input(p_outm),
			       jack_port_ensure_monitor(p_outm, 1));
		}
		if (p_in != NULL) {
			printf(",\"request_monitor_in_rc\":%d,\"monitoring_input_in\":%d",
			       jack_port_request_monitor(p_in, 1), jack_port_monitoring_input(p_in));
		}
		/* connections of my own ports (expect empty) */
		printf(",\"out_connections\":");
		{
			const char **cn = p_out ? jack_port_get_connections(p_out) : NULL;
			int k = 0; printf("[");
			if (cn) { for (; cn[k]; k++) { if (k) putchar(','); jstr(cn[k]); } jack_free(cn); }
			printf("],\"out_connected\":%d", p_out ? jack_port_connected(p_out) : -1);
		}
		/* port census: visibility of foreign/native ports */
		{
			const char **all = jack_get_ports(c, NULL, NULL, 0);
			const char **outs = jack_get_ports(c, NULL, NULL, JackPortIsOutput);
			const char **ins = jack_get_ports(c, NULL, NULL, JackPortIsInput);
			const char **phys = jack_get_ports(c, NULL, NULL, JackPortIsPhysical);
			const char **pat = jack_get_ports(c, "r95s", NULL, 0);
			const char **dsp = jack_get_ports(c, NULL, "32 bit float mono audio", 0);
			int na = 0, no = 0, ni = 0, np = 0, npat = 0, ndsp = 0;
			if (all) for (na = 0; all[na]; na++);
			if (outs) for (no = 0; outs[no]; no++);
			if (ins) for (ni = 0; ins[ni]; ni++);
			if (phys) for (np = 0; phys[np]; np++);
			if (pat) for (npat = 0; pat[npat]; npat++);
			if (dsp) for (ndsp = 0; dsp[ndsp]; ndsp++);
			printf(",\"census\":{\"all\":%d,\"outputs\":%d,\"inputs\":%d,"
			       "\"physical\":%d,\"pattern_r95s\":%d,\"dsp_type\":%d",
			       na, no, ni, np, npat, ndsp);
			printf(",\"pattern_r95s_list\":[");
			if (pat) { for (int k = 0; pat[k]; k++) { if (k) putchar(','); jstr(pat[k]); } }
			printf("],\"first40\":[");
			if (all) { for (int k = 0; k < na && k < 40; k++) { if (k) putchar(','); jstr(all[k]); } }
			printf("]}");
			if (all) jack_free(all);
			if (outs) jack_free(outs);
			if (ins) jack_free(ins);
			if (phys) jack_free(phys);
			if (pat) jack_free(pat);
			if (dsp) jack_free(dsp);
		}
		/* resolve census: for each pattern hit, what name resolves and what aliases exist */
		{
			const char **pat2 = jack_get_ports(c, "r95s", NULL, 0);
			printf(",\"resolve\":[");
			int k = 0;
			if (pat2) {
				for (int i = 0; pat2[i] && i < 12; i++) {
					jack_port_t *pp = jack_port_by_name(c, pat2[i]);
					char *al[2] = {NULL, NULL};
					int na = pp ? jack_port_get_aliases(pp, al) : -1;
					if (k++) putchar(',');
					printf("{\"name\":");
					jstr(pat2[i]);
					printf(",\"found\":%s,\"flags\":%lu,\"aliases\":[",
					       pp ? "true" : "false",
					       (unsigned long)(pp ? jack_port_flags(pp) : 0));
					for (int j = 0; j < na && j < 2; j++) {
						if (j) putchar(',');
						jstr(al[j]);
					}
					printf("]}");
				}
				jack_free(pat2);
			}
			printf("]");
		}
		/* optional: jack_connect my out -> argv[3] (done early, held through the run) */
		if (xc_done) {
			printf(",\"xconnect\":{\"dst\":");
			jstr(xc_dst);
			printf(",\"by_name_found\":%s", xc_found ? "true" : "false");
			printf(",\"connect_rc\":%d", xc_rc);
			printf(",\"connected\":%d", jack_port_connected(p_out));
			printf(",\"conns\":[");
			for (int k = 0; k < xc_conns_n; k++) {
				if (k) putchar(',');
				jstr(xc_conns[k]);
			}
			printf("]");
			if (argc > 4 && !strcmp(argv[4], "disconnect")) {
				printf(",\"disconnect_rc\":%d", jack_disconnect(c, jack_port_name(p_out), xc_dst));
			}
			printf("}");
		}
		printf("}\n");
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "rtprio")) {
		jack_client_t *c = open_client("r95s_rtp", &status);
		g_client = c;
		printf("R95JSON {\"mode\":\"rtprio\",\"status\":%d,", (int)status);
		print_common(c);
		jack_activate(c);
		printf(",\"samples\":[");
		for (int i = 0; i < 6; i++) {
			printf("%s[%d,%d]", i ? "," : "",
			       jack_client_real_time_priority(c),
			       jack_client_max_real_time_priority(c));
			usleep(120000);
		}
		printf("],\"is_realtime_live\":%d,\"cpu_load_live\":%.6f}\n",
		       jack_is_realtime(c), jack_cpu_load(c));
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "tone") || !strcmp(mode, "stall")) {
		jack_client_t *c = open_client("r95s_probe", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		p_in = jack_port_register(c, "in", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
		jack_nframes_t fs = jack_get_sample_rate(c);
		if (fs == 0) fs = 48000;
		g_dphase = 2.0 * M_PI * 997.0 / (double)fs;
		C.g_coef = 2.0 * cos(2.0 * M_PI * 997.0 / (double)fs);
		jack_set_process_callback(c, process_cb, NULL);
		jack_set_xrun_callback(c, xrun_cb, NULL);
		jack_set_buffer_size_callback(c, bufsize_cb, NULL);
		jack_set_sample_rate_callback(c, srate_cb, NULL);
		jack_set_graph_order_callback(c, graph_cb, NULL);
		jack_set_port_registration_callback(c, reg_cb, NULL);
		jack_set_port_connect_callback(c, conn_cb, NULL);
		jack_set_freewheel_callback(c, fw_cb, NULL);
		if (!strcmp(mode, "stall")) {
			g_stall_every = argc > 3 ? strtoul(argv[3], NULL, 10) : 4;
			g_stall_us = argc > 4 ? strtoul(argv[4], NULL, 10) : 150000;
		}
		jack_activate(c);
		/* optional target: jack_connect own out -> argv[5] */
		int conn_rc = -999;
		if (argc > 5 && argv[5][0]) {
			conn_rc = jack_connect(c, jack_port_name(p_out), argv[5]);
		}
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		double wall = mono_us() - t0;
		printf("R95JSON {\"mode\":\"%s\",\"status\":%d,", mode, (int)status);
		print_common(c);
		printf(",\"wall_us\":%.1f,\"conn_rc\":%d,\"out_name\":", wall, conn_rc);
		jstr(jack_port_name(p_out));
		printf(",\"in_name\":");
		jstr(jack_port_name(p_in));
		printf(",");
		print_counters();
		printf(",\"srate_live\":%u,\"bufsize_live\":%u", jack_get_sample_rate(c), jack_get_buffer_size(c));
		print_cycle_times(c);
		printf(",\"xrun_delayed_usecs\":%.3f,\"max_delayed_usecs\":%.3f",
		       jack_get_xrun_delayed_usecs(c), jack_get_max_delayed_usecs(c));
		printf(",\"transport_state\":%d", (int)jack_transport_query(c, NULL));
		printf("}\n");
		fflush(stdout);
		jack_deactivate(c);
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "bufsize")) {
		jack_nframes_t n1 = argc > 3 ? (jack_nframes_t)strtoul(argv[3], NULL, 10) : 2048;
		jack_nframes_t n2 = argc > 4 ? (jack_nframes_t)strtoul(argv[4], NULL, 10) : 0;
		jack_client_t *c = open_client("r95s_buf", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		jack_set_buffer_size_callback(c, bufsize_cb, NULL);
		printf("R95JSON {\"mode\":\"bufsize\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"srate_inactive\":%u,\"bufsize_inactive\":%u,"
		       "\"set_inactive_rc\":%d,\"bufsize_after_set_inactive\":%u",
		       jack_get_sample_rate(c), jack_get_buffer_size(c),
		       jack_set_buffer_size(c, n1), jack_get_buffer_size(c));
		jack_activate(c);
		printf(",\"bufsize_activated\":%u,\"srate_active\":%u",
		       jack_get_buffer_size(c), jack_get_sample_rate(c));
		print_cycle_times(c);
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		printf(",\"bufsize_live\":%u,\"bufsize_cbs\":%lu,\"last_bufsize_cb\":%lu",
		       jack_get_buffer_size(c), C.bufsize_cbs, C.last_bufsize);
		print_cycle_times(c);
		if (n2 > 0) {
			printf(",\"set_active_rc\":%d,\"set_active_to\":%u", jack_set_buffer_size(c, n2), n2);
			double t1 = mono_us();
			while (!g_stop && mono_us() - t1 < 0.7e6) usleep(20000);
			printf(",\"bufsize_after_set_active\":%u,\"bufsize_cbs_after\":%lu,"
			       "\"last_bufsize_cb_after\":%lu",
			       jack_get_buffer_size(c), C.bufsize_cbs, C.last_bufsize);
			print_cycle_times(c);
		}
		printf("}\n");
		fflush(stdout);
		jack_deactivate(c);
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "latency")) {
		jack_client_t *c = open_client("r95s_lat", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		p_in = jack_port_register(c, "in", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
		printf("R95JSON {\"mode\":\"latency\",\"status\":%d,", (int)status);
		print_common(c);
		print_latency(p_out, "out_before");
		print_latency(p_in, "in_before");
		{
			jack_latency_range_t r = {100, 200};
			jack_port_set_latency_range(p_out, JackCaptureLatency, &r);
			r.min = 10; r.max = 20;
			jack_port_set_latency_range(p_out, JackPlaybackLatency, &r);
		}
		print_latency(p_out, "out_after_set");
		printf(",\"recompute_rc\":%d", jack_recompute_total_latency(c, p_out));
		jack_activate(c);
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		print_latency(p_out, "out_active");
		print_latency(p_in, "in_active");
		printf(",\"bufsize\":%u,\"srate\":%u}\n", jack_get_buffer_size(c), jack_get_sample_rate(c));
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "transport")) {
		jack_client_t *c = open_client("r95s_tr", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		jack_position_t pos;
		jack_transport_state_t st0 = jack_transport_query(c, &pos);
		printf("R95JSON {\"mode\":\"transport\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"state_before_activate\":%d,\"pos_frame_before\":%u", (int)st0, pos.frame);
		jack_activate(c);
		int tconn_rc = -999;
		if (argc > 3 && argv[3][0])
			tconn_rc = jack_connect(c, jack_port_name(p_out), argv[3]);
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		jack_transport_state_t st1 = jack_transport_query(c, &pos);
		printf(",\"state_after_activate\":%d,\"frame_after\":%u,\"usecs\":%llu,"
		       "\"frame_rate\":%u,\"valid\":%u,\"current_frame\":%u",
		       (int)st1, pos.frame, (unsigned long long)pos.usecs,
		       pos.frame_rate, (unsigned)pos.valid, jack_get_current_transport_frame(c));
		jack_transport_start(c);
		double t1 = mono_us();
		while (!g_stop && mono_us() - t1 < 0.5e6) usleep(20000);
		jack_transport_state_t st2 = jack_transport_query(c, &pos);
		printf(",\"state_after_start\":%d,\"frame_after_start\":%u", (int)st2, pos.frame);
		jack_transport_stop(c);
		double t2 = mono_us();
		while (!g_stop && mono_us() - t2 < 0.5e6) usleep(20000);
		jack_transport_state_t st3 = jack_transport_query(c, &pos);
		printf(",\"state_after_stop\":%d,\"frame_after_stop\":%u", (int)st3, pos.frame);
		int locate_rc = jack_transport_locate(c, 123456);
		jack_transport_state_t st4 = jack_transport_query(c, &pos);
		printf(",\"state_after_locate\":%d,\"frame_after_locate\":%u,"
		       "\"current_after_locate\":%u,\"locate_rc\":%d",
		       (int)st4, pos.frame, jack_get_current_transport_frame(c), locate_rc);
		jack_position_t tp = {0};
		tp.frame = 48000; tp.valid = JackPositionBBT;
		int rep_rc = jack_transport_reposition(c, &tp);
		printf(",\"reposition_rc\":%d", rep_rc);
		jack_transport_state_t st5 = jack_transport_query(c, &pos);
		printf(",\"state_after_reposition\":%d,\"frame_after_reposition\":%u", (int)st5, pos.frame);
		printf(",\"tconn_rc\":%d,\"out_name\":", tconn_rc);
		jstr(jack_port_name(p_out));
		printf(",\"out_connected\":%d", jack_port_connected(p_out));
		printf("}\n");
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "metadata")) {
		jack_client_t *c = open_client("r95s_meta", &status);
		g_client = c;
		p_out = jack_port_register(c, "out", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
		jack_uuid_t cu = 0;
		char *us = jack_client_get_uuid(c);
		if (us) { jack_uuid_parse(us, &cu); jack_free(us); }
		jack_uuid_t pu = p_out ? jack_port_uuid(p_out) : 0;
		char cub[64], pub[64];
		jack_uuid_unparse(cu, cub); jack_uuid_unparse(pu, pub);
		jack_activate(c);
		double t0 = mono_us();
		printf("R95JSON {\"mode\":\"metadata\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"port_uuid\":\"%s\",\"set_client_rc\":%d,"
		       "\"set_port_rc\":%d",
		       pub,
		       jack_set_property(c, cu, "r95s/key1", "value1", "text/plain"),
		       jack_set_property(c, pu, "r95s/portkey", "portval", "text/plain"));
		char *v = NULL, *t = NULL;
		int gr = jack_get_property(cu, "r95s/key1", &v, &t);
		printf(",\"get_client_rc\":%d,\"get_client_value\":", gr);
		jstr(v);
		printf(",\"get_client_type\":");
		jstr(t);
		if (v) jack_free(v);
		if (t) jack_free(t);
		v = NULL; t = NULL;
		int gr2 = jack_get_property(pu, "r95s/portkey", &v, &t);
		printf(",\"get_port_rc\":%d,\"get_port_value\":", gr2);
		jstr(v);
		printf(",\"get_port_type\":");
		jstr(t);
		if (v) jack_free(v);
		if (t) jack_free(t);
		int gm = jack_get_property(cu, "r95s/missing", &v, &t);
		printf(",\"get_missing_rc\":%d", gm);
		/* all properties: count + own subjects */
		jack_description_t *descs = NULL;
		int nd = jack_get_all_properties(&descs);
		int own = 0;
		if (nd > 0 && descs) {
			for (int i = 0; i < nd; i++)
				if (jack_uuid_compare(descs[i].subject, cu) == 0 ||
				    jack_uuid_compare(descs[i].subject, pu) == 0) own++;
			for (int i = 0; i < nd; i++) jack_free_description(&descs[i], 0);
			jack_free(descs);
		}
		printf(",\"all_desc_count\":%d,\"own_desc_count\":%d", nd, own);
		while (!g_stop && mono_us() - t0 < dur * 1e6) usleep(20000);
		printf(",\"remove_client_rc\":%d", jack_remove_property(c, cu, "r95s/key1"));
		usleep(250000);
		v = NULL; t = NULL;
		printf(",\"get_after_remove_rc\":%d", jack_get_property(cu, "r95s/key1", &v, &t));
		printf(",\"get_after_remove_value\":");
		jstr(v);
		if (v) jack_free(v);
		if (t) jack_free(t);
		printf(",\"remove_port_rc\":%d", jack_remove_property(c, pu, "r95s/portkey"));
		usleep(250000);
		v = NULL; t = NULL;
		printf(",\"get_port_after_remove_rc\":%d", jack_get_property(pu, "r95s/portkey", &v, &t));
		if (v) jack_free(v);
		if (t) jack_free(t);
		printf(",\"client_uuid_index\":%u,\"port_uuid_index\":%u",
		       jack_uuid_to_index(cu), jack_uuid_to_index(pu));
		printf("}\n");
		fflush(stdout);
		jack_deactivate(c);
		jack_client_close(c);
		return 0;
	}

	if (!strcmp(mode, "xconnect")) {
		/* xconnect <src> <dst> <hold_s> — open a client, connect two ports by name */
		if (argc < 4) { printf("R95JSON {\"mode\":\"xconnect\",\"error\":\"argv\"}\n"); return 2; }
		jack_client_t *c = open_client("r95s_xc", &status);
		g_client = c;
		jack_port_t *src = jack_port_by_name(c, argv[2]);
		jack_port_t *dst = jack_port_by_name(c, argv[3]);
		printf("R95JSON {\"mode\":\"xconnect\",\"status\":%d,", (int)status);
		print_common(c);
		printf(",\"src\":");
		jstr(argv[2]);
		printf(",\"dst\":");
		jstr(argv[3]);
		printf(",\"src_found\":%s,\"dst_found\":%s,"
		       "\"src_flags\":%lu,\"dst_flags\":%lu,"
		       "\"src_type\":", src ? "true" : "false", dst ? "true" : "false",
		       (unsigned long)(src ? jack_port_flags(src) : 0), (unsigned long)(dst ? jack_port_flags(dst) : 0));
		jstr(src ? jack_port_type(src) : "");
		printf(",\"dst_type\":");
		jstr(dst ? jack_port_type(dst) : "");
		printf(",\"connect_rc\":%d", jack_connect(c, argv[2], argv[3]));
		double hold = argc > 4 ? atof(argv[4]) : 0.5;
		double t0 = mono_us();
		while (!g_stop && mono_us() - t0 < hold * 1e6) usleep(20000);
		printf(",\"disconnect_rc\":%d", jack_disconnect(c, argv[2], argv[3]));
		printf("}\n");
		jack_client_close(c);
		return 0;
	}

	printf("R95JSON {\"mode\":\"unknown\",\"mode_arg\":");
	jstr(mode);
	printf("}\n");
	return 2;
}
