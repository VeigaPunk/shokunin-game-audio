/* r96-scout own libpulse client — cork / trigger / prebuf / record-cork probes.
 *
 * Linked against the host libpulse 17.0 (protocol 35) served by pipewire-pulse
 * 1.6.8. Seat-owned stream names only (r96s_*). Emits one JSON line per event
 * with CLOCK_MONOTONIC milliseconds, so the driver can correlate with its own
 * monotonic clock and with monitor captures.
 *
 * Usage: r96pulse MODE [--device NAME] [--tlength B] [--prebuf B]
 *        [--tone-ms MS] [--chunk-ms MS] [--period-ms MS] [--hold-ms MS]
 *        [--tail-ms MS] [--label L]
 * Modes: cork trigger prebuf prebuf0 record resolve
 */
#include <math.h>
#include <stdint.h>
#include <pulse/pulseaudio.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static pa_mainloop *ml;
static pa_context *ctx;
static pa_stream *st;
static int done_flag;

static double mono_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

static void ev(const char *name, const char *extra) {
    printf("{\"ev\":\"%s\",\"t_ms\":%.2f%s%s}\n", name, mono_ms(),
           extra ? "," : "", extra ? extra : "");
    fflush(stdout);
}

static void wait_ms(double ms) {
    double end = mono_ms() + ms;
    while (mono_ms() < end) {
        int r;
        if (pa_mainloop_iterate(ml, 0, &r) < 0)
            break;
        struct timespec ts = {0, 2000000}; /* 2 ms */
        nanosleep(&ts, NULL);
    }
}

static void ctx_state_cb(pa_context *c, void *u) { (void)c; (void)u; }
static void stream_state_cb(pa_stream *s, void *u) { (void)s; (void)u; }
static void stream_success_cb(pa_stream *s, int success, void *u) {
    (void)s; (void)u;
    if (!success) ev("op_failed", NULL);
}

static int wait_ctx_ready(void) {
    for (;;) {
        pa_context_state_t cs = pa_context_get_state(ctx);
        if (cs == PA_CONTEXT_READY) return 0;
        if (!PA_CONTEXT_IS_GOOD(cs)) return -1;
        wait_ms(20);
    }
}

static int wait_stream_ready(void) {
    for (;;) {
        pa_stream_state_t ss = pa_stream_get_state(st);
        if (ss == PA_STREAM_READY) return 0;
        if (!PA_STREAM_IS_GOOD(ss)) return -1;
        wait_ms(20);
    }
}

static void write_tone(double amp, int ms, int chunk_ms) {
    pa_sample_spec ss = *pa_stream_get_sample_spec(st);
    size_t frame = pa_frame_size(&ss);
    int total_frames = (int)((long long)ss.rate * ms / 1000);
    int chunk_frames = (int)((long long)ss.rate * chunk_ms / 1000);
    if (chunk_frames < 1) chunk_frames = 1;
    unsigned char *buf = malloc((size_t)chunk_frames * frame);
    long long phase = 0;
    int written = 0;
    while (written < total_frames) {
        int n = total_frames - written;
        if (n > chunk_frames) n = chunk_frames;
        for (int i = 0; i < n; i++) {
            double v = amp * 32767.0 * sin(2.0 * 3.14159265358979 * 997.0 * (phase + i) / ss.rate);
            int16_t s = (int16_t)(v > 32767 ? 32767 : (v < -32768 ? -32768 : (int)(v >= 0 ? v + 0.5 : v - 0.5)));
            memcpy(buf + (size_t)i * frame, &s, sizeof(s));
            if (frame > 2) memset(buf + (size_t)i * frame + 2, 0, frame - 2);
        }
        size_t len = (size_t)n * frame;
        int tries = 0;
        while (pa_stream_write(st, buf, len, NULL, 0, PA_SEEK_RELATIVE) < 0) {
            if (++tries > 400) { ev("write_stuck", NULL); break; }
            wait_ms(5);
        }
        written += n;
        phase += n;
    }
    free(buf);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: r96pulse MODE [opts]\n"); return 2; }
    const char *mode = argv[1];
    const char *device = NULL, *label = "r96s_pulse";
    long tlength = -1, prebuf = -1;
    int tone_ms = 1500, chunk_ms = 500, period_ms = 0, hold_ms = 1200, tail_ms = 800;
    for (int i = 2; i + 1 < argc; i += 2) {
        if (!strcmp(argv[i], "--device")) device = argv[i + 1];
        else if (!strcmp(argv[i], "--tlength")) tlength = atol(argv[i + 1]);
        else if (!strcmp(argv[i], "--prebuf")) prebuf = atol(argv[i + 1]);
        else if (!strcmp(argv[i], "--tone-ms")) tone_ms = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--chunk-ms")) chunk_ms = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--period-ms")) period_ms = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--hold-ms")) hold_ms = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--tail-ms")) tail_ms = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--label")) label = argv[i + 1];
    }

    ev("start", NULL);
    ml = pa_mainloop_new();
    pa_mainloop_api *api = pa_mainloop_get_api(ml);
    ctx = pa_context_new(api, label);
    pa_context_set_state_callback(ctx, ctx_state_cb, NULL);
    if (pa_context_connect(ctx, NULL, 0, NULL) < 0) { ev("connect_failed", NULL); return 1; }
    if (wait_ctx_ready() < 0) { ev("ctx_failed", NULL); return 1; }
    ev("ctx_ready", NULL);

    pa_sample_spec ss = {.format = PA_SAMPLE_S16LE, .rate = 48000, .channels = 1};
    pa_channel_map map;
    pa_channel_map_init_mono(&map);
    pa_buffer_attr attr;
    attr.maxlength = (uint32_t)-1;
    attr.tlength = (uint32_t)tlength;
    attr.prebuf = (uint32_t)prebuf;
    attr.minreq = (uint32_t)-1;
    attr.fragsize = (uint32_t)-1;

    if (!strcmp(mode, "record")) {
        st = pa_stream_new(ctx, label, &ss, &map);
        pa_stream_set_state_callback(st, stream_state_cb, NULL);
        attr.fragsize = 4800;
        int rc = pa_stream_connect_record(st, device, &attr,
                PA_STREAM_START_CORKED | PA_STREAM_ADJUST_LATENCY);
        ev("connect_record", NULL);
        if (rc < 0 || wait_stream_ready() < 0) { ev("stream_failed", NULL); return 1; }
        ev("stream_ready", NULL);
        wait_ms(hold_ms);
        size_t rd = pa_stream_readable_size(st);
        char extra[64];
        snprintf(extra, sizeof(extra), "\"readable_corked\":%zu,\"is_corked\":%d",
                 rd, pa_stream_is_corked(st));
        ev("corked_check", extra);
        pa_stream_cork(st, 0, stream_success_cb, NULL);
        ev("uncork", NULL);
        wait_ms(tail_ms);
        rd = pa_stream_readable_size(st);
        snprintf(extra, sizeof(extra), "\"readable_uncorked\":%zu,\"is_corked\":%d",
                 rd, pa_stream_is_corked(st));
        ev("uncorked_check", extra);
        /* drain a bit to prove data is really there */
        int peeks = 0, bytes = 0;
        for (int i = 0; i < 50; i++) {
            const void *p; size_t n;
            if (pa_stream_peek(st, &p, &n) < 0) break;
            if (n) { bytes += (int)n; peeks++; }
            pa_stream_drop(st);
            wait_ms(10);
            if (bytes > 48000) break;
        }
        snprintf(extra, sizeof(extra), "\"peek_bytes\":%d,\"peeks\":%d", bytes, peeks);
        ev("drained", extra);
        pa_stream_disconnect(st);
        pa_context_disconnect(ctx);
        ev("end", NULL);
        return 0;
    }

    /* playback modes */
    pa_stream_flags_t flags = 0;
    if (!strcmp(mode, "cork") || !strcmp(mode, "trigger") || !strcmp(mode, "resolve"))
        flags |= PA_STREAM_START_CORKED;
    if (!strcmp(mode, "prebuf") || !strcmp(mode, "prebuf0"))
        flags |= PA_STREAM_ADJUST_LATENCY;

    st = pa_stream_new(ctx, label, &ss, &map);
    pa_stream_set_state_callback(st, stream_state_cb, NULL);
    int rc = pa_stream_connect_playback(st, device, &attr, flags, NULL, NULL);
    ev("connect_playback", NULL);
    if (rc < 0 || wait_stream_ready() < 0) { ev("stream_failed", NULL); return 1; }
    {
        char extra[256];
        pa_usec_t usec = 0; int neg = 0;
        pa_stream_get_latency(st, &usec, &neg);
        const pa_buffer_attr *a = pa_stream_get_buffer_attr(st);
        snprintf(extra, sizeof(extra),
                 "\"is_corked\":%d,\"writable\":%zu,\"latency_usec\":%lu,\"neg\":%d,"
                 "\"attr_tlength\":%u,\"attr_prebuf\":%u,\"attr_minreq\":%u,\"attr_maxlength\":%u",
                 pa_stream_is_corked(st), pa_stream_writable_size(st), usec, neg,
                 a ? a->tlength : 0, a ? a->prebuf : 0, a ? a->minreq : 0, a ? a->maxlength : 0);
        ev("stream_ready", extra);
    }

    if (!strcmp(mode, "prebuf") || !strcmp(mode, "prebuf0")) {
        /* slow feed: chunk_ms of tone every period_ms */
        int total = tone_ms;
        int fed = 0;
        while (fed < total) {
            int n = chunk_ms;
            if (fed + n > total) n = total - fed;
            /* feed n ms by writing chunk_ms-sized writes */
            write_tone(0.5, n, n > 0 ? n : 1);
            fed += n;
            char extra[64];
            snprintf(extra, sizeof(extra), "\"fed_ms\":%d", fed);
            ev("fed", extra);
            wait_ms(period_ms > 0 ? period_ms : 250);
        }
        wait_ms(tail_ms);
    } else {
        write_tone(0.5, tone_ms, chunk_ms);
        ev("written", NULL);
        wait_ms(hold_ms);
        if (!strcmp(mode, "cork")) {
            pa_stream_cork(st, 0, stream_success_cb, NULL);
            ev("uncork", NULL);
        } else if (!strcmp(mode, "trigger")) {
            pa_stream_trigger(st, stream_success_cb, NULL);
            ev("trigger", NULL);
        }
        wait_ms(tail_ms);
    }
    {
        char extra[128];
        pa_usec_t usec = 0; int neg = 0;
        pa_stream_get_latency(st, &usec, &neg);
        snprintf(extra, sizeof(extra), "\"is_corked\":%d,\"latency_usec\":%lu,\"neg\":%d",
                 pa_stream_is_corked(st), usec, neg);
        ev("final", extra);
    }
    pa_stream_disconnect(st);
    pa_context_disconnect(ctx);
    ev("end", NULL);
    return 0;
}
