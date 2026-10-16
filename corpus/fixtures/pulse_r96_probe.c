/* pulse_r96_probe.c — the r96 author's own libpulse client.
 *
 * WHY THIS FILE EXISTS: the pulse client surface has a whole class of
 * behaviours that no shipped CLI can arm — PA_STREAM_START_CORKED,
 * pa_stream_trigger, an explicit prebuf=0 buffer attribute, a corked
 * RECORD stream, and the RETURN CODE of pa_stream_get_latency. pacat
 * exposes none of them. This instrument is the only way the r96 family
 * can measure the cork/trigger/prebuf/record/latency-query laws; the
 * build is done at run time by measure_audio.py (--probe-pulsecli-r96)
 * and a failed build is a NAMED coverage block, never a silent green.
 *
 * The r96 boundary's instrument (a sibling seat's copy) is the shape
 * this one follows: a bounded, self-reporting client that prints one
 * `EV key=value ...` line per event on stdout and a final `SUMMARY`
 * line. Every line is data; the Python side owns the verdicts.
 *
 * Usage:
 *   pulse_r96_probe --mode {cork|trigger|prebuf|record|latency}
 *                   [--label NAME] [--device DEV] [--server SRV]
 *                   [--amp F] [--hold-ms N] [--feed-ms N] [--chunk-ms N]
 *                   [--prebuf N] [--start-corked 0|1] [--seconds F]
 *                   [--latency-hz HZ] [--drain-max B]
 *
 * Modes:
 *   cork     playback: START_CORKED, feed, hold, pa_stream_cork(0)
 *   trigger  playback: START_CORKED, feed, hold, pa_stream_trigger()
 *   prebuf   playback: explicit attr prebuf (--prebuf), slow or fast feed
 *   record   capture: START_CORKED, readable while corked, uncork, drain
 *   latency  playback: sample pa_stream_get_latency with the rc recorded
 *
 * Build: gcc -O1 -o pulse_r96_probe pulse_r96_probe.c -lpulse
 */
#include <pulse/pulseaudio.h>
#include <pulse/error.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <math.h>

static pa_mainloop *m = NULL;
static pa_context *ctx = NULL;
static pa_stream *st = NULL;
static volatile sig_atomic_t stop_now = 0;
static double t0 = 0.0;

static void on_signal(int sig) { (void)sig; stop_now = 1; }

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static void ev(const char *fmt, ...)
{
    va_list ap;
    printf("EV t=%.3f ", now_s() - t0);
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    printf("\n");
    fflush(stdout);
}

/* one nonblocking mainloop turn (no callbacks are registered: every
 * state transition is polled, which keeps the client readable and
 * immune to callback-signature mistakes) */
static void tick(void)
{
    if (m)
        pa_mainloop_iterate(m, 0, NULL);
    usleep(10000);
}

static int wait_context(double bound_s)
{
    double deadline = now_s() + bound_s;
    while (now_s() < deadline && !stop_now) {
        pa_context_state_t s = pa_context_get_state(ctx);
        if (s == PA_CONTEXT_READY)
            return 0;
        if (!PA_CONTEXT_IS_GOOD(s)) {
            ev("context state=%s", pa_strerror(pa_context_errno(ctx)));
            return -1;
        }
        tick();
    }
    ev("context timeout");
    return -1;
}

static int wait_stream(double bound_s)
{
    double deadline = now_s() + bound_s;
    while (now_s() < deadline && !stop_now) {
        pa_stream_state_t s = pa_stream_get_state(st);
        if (s == PA_STREAM_READY)
            return 0;
        if (!PA_STREAM_IS_GOOD(s)) {
            ev("stream error=%s", pa_strerror(pa_context_errno(pa_stream_get_context(st))));
            return -1;
        }
        tick();
    }
    ev("stream timeout");
    return -1;
}

static void sample_latency(const char *phase)
{
    pa_usec_t usec = 0;
    int negative = 0;
    int rc = pa_stream_get_latency(st, &usec, &negative);
    ev("latency phase=%s rc=%d usec=%llu negative=%d err=%s", phase, rc,
       (unsigned long long)usec, negative,
       rc < 0 ? pa_strerror(rc) : "-");
}

int main(int argc, char **argv)
{
    const char *mode = "cork", *label = "r96a_pulse", *device = NULL;
    const char *server = NULL;
    double amp = 0.25, seconds = 1.2, hold_ms = 1200.0, feed_ms = 0.0;
    double chunk_ms = 0.0, latency_hz = 5.0;
    long prebuf = -1, start_corked = 1, drain_max = 1 << 20;
    const char *attr_mode = "full";
    int i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--mode") && i + 1 < argc) mode = argv[++i];
        else if (!strcmp(argv[i], "--label") && i + 1 < argc) label = argv[++i];
        else if (!strcmp(argv[i], "--device") && i + 1 < argc) device = argv[++i];
        else if (!strcmp(argv[i], "--server") && i + 1 < argc) server = argv[++i];
        else if (!strcmp(argv[i], "--amp") && i + 1 < argc) amp = atof(argv[++i]);
        else if (!strcmp(argv[i], "--seconds") && i + 1 < argc) seconds = atof(argv[++i]);
        else if (!strcmp(argv[i], "--hold-ms") && i + 1 < argc) hold_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--feed-ms") && i + 1 < argc) feed_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--chunk-ms") && i + 1 < argc) chunk_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--latency-hz") && i + 1 < argc) latency_hz = atof(argv[++i]);
        else if (!strcmp(argv[i], "--prebuf") && i + 1 < argc) prebuf = atol(argv[++i]);
        else if (!strcmp(argv[i], "--start-corked") && i + 1 < argc) start_corked = atol(argv[++i]);
        else if (!strcmp(argv[i], "--drain-max") && i + 1 < argc) drain_max = atol(argv[++i]);
        else if (!strcmp(argv[i], "--attr-mode") && i + 1 < argc) attr_mode = argv[++i];
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 2; }
    }
    t0 = now_s();
    signal(SIGTERM, on_signal);
    signal(SIGINT, on_signal);

    m = pa_mainloop_new();
    if (!m) { fprintf(stderr, "mainloop\n"); return 3; }
    pa_proplist *pl = pa_proplist_new();
    pa_proplist_sets(pl, PA_PROP_APPLICATION_NAME, label);
    /* the r90 C8/C9 hygiene: a probe stream must not touch the
     * operator's WirePlumber restore state */
    pa_proplist_sets(pl, "state.restore-props", "false");
    ctx = pa_context_new_with_proplist(pa_mainloop_get_api(m), label, pl);
    pa_proplist_free(pl);
    if (!ctx) { fprintf(stderr, "context\n"); return 3; }
    if (pa_context_connect(ctx, server, PA_CONTEXT_NOFLAGS, NULL) < 0) {
        fprintf(stderr, "connect: %s\n", pa_strerror(pa_context_errno(ctx)));
        return 3;
    }
    ev("connect label=%s device=%s mode=%s server=%s", label,
       device ? device : "(default)", mode, server ? server : "(default)");
    if (wait_context(10.0) != 0)
        return 3;
    ev("context ready");

    pa_sample_spec ss;
    ss.format = PA_SAMPLE_S16LE;
    ss.rate = 48000;
    ss.channels = 1;

    pa_channel_map cm;
    pa_channel_map_init_mono(&cm);

    pa_stream_flags_t flags = PA_STREAM_NOFLAGS;
    if (start_corked)
        flags |= PA_STREAM_START_CORKED;

    pa_buffer_attr attr;
    attr.maxlength = (uint32_t)-1;
    attr.tlength = (uint32_t)-1;
    attr.prebuf = (prebuf >= 0) ? (uint32_t)prebuf : (uint32_t)-1;
    attr.minreq = (uint32_t)-1;
    attr.fragsize = (uint32_t)-1;

    st = pa_stream_new(ctx, label, &ss, &cm);
    if (!st) { fprintf(stderr, "stream\n"); return 3; }

    if (!strcmp(mode, "record")) {
        attr.fragsize = (uint32_t)(48000 * 2);   /* 1 s of s16 mono */
        pa_buffer_attr *rattr = &attr;
        if (!strcmp(attr_mode, "none"))
            rattr = NULL;
        else if (!strcmp(attr_mode, "fragonly")) {
            attr.maxlength = (uint32_t)-1;
            attr.tlength = (uint32_t)-1;
            attr.prebuf = (uint32_t)-1;
            attr.minreq = (uint32_t)-1;
        }
        if (pa_stream_connect_record(st, device, rattr, flags) < 0) {
            ev("connect_record error=%s", pa_strerror(pa_context_errno(pa_stream_get_context(st))));
            return 3;
        }
    } else {
        if (pa_stream_connect_playback(st, device, &attr, flags, NULL,
                                       NULL) < 0) {
            ev("connect_playback error=%s",
               pa_strerror(pa_context_errno(pa_stream_get_context(st))));
            return 3;
        }
    }
    if (wait_stream(10.0) != 0)
        return 3;
    ev("stream ready corked=%d", start_corked ? 1 : 0);
    sample_latency("ready");

    if (!strcmp(mode, "record")) {
        size_t rd_corked = pa_stream_readable_size(st);
        ev("readable phase=corked bytes=%zu", rd_corked);
        /* hold the cork so a server-side snapshot can witness
         * `Corked: true` on the source-output, and so the readable size
         * is sampled over a real window (it must stay 0) */
        double cork_deadline = now_s() + (hold_ms / 1000.0);
        size_t corked_peak = 0;
        while (now_s() < cork_deadline && !stop_now) {
            size_t r = pa_stream_readable_size(st);
            if (r > corked_peak)
                corked_peak = r;
            tick();
        }
        ev("readable phase=corked bytes=%zu peak=%zu", rd_corked,
           corked_peak);
        if (start_corked) {
            pa_operation *op = pa_stream_cork(st, 0, NULL, NULL);
            if (op) pa_operation_unref(op);
            ev("uncork");
        }
        /* PHASE 1: sample the readable size WITHOUT draining — the
         * record flow gate is about data becoming readable after the
         * uncork, and a client that drains continuously would only ever
         * report its own loop granularity. */
        double hold_deadline = now_s() + 2.5;
        size_t peak = 0;
        while (now_s() < hold_deadline && !stop_now) {
            size_t r = pa_stream_readable_size(st);
            if (r > peak) {
                peak = r;
                ev("readable phase=uncorked peak=%zu", peak);
            }
            tick();
        }
        /* PHASE 2: drain (bounded) — the bytes really are there */
        double deadline = now_s() + 1.5;
        size_t drained = 0;
        while (now_s() < deadline && !stop_now) {
            size_t r = pa_stream_readable_size(st);
            if (r > 0) {
                const void *data = NULL;
                size_t n = 0;
                if (pa_stream_peek(st, &data, &n) < 0) {
                    ev("peek error=%s", pa_strerror(pa_context_errno(pa_stream_get_context(st))));
                    break;
                }
                if (n) {
                    drained += n;
                    pa_stream_drop(st);
                }
                if (drained >= (size_t)drain_max)
                    break;
            }
            tick();
        }
        sample_latency("final");
        ev("readable phase=drained drained=%zu", drained);
        printf("SUMMARY mode=record rc=0 drained=%zu peak=%zu\n",
               drained, peak);
        fflush(stdout);
        goto done;
    }

    /* playback: generate the tone once (s16 mono, 997 Hz) */
    size_t total_frames = (size_t)(48000 * seconds);
    size_t total_bytes = total_frames * 2;
    int16_t *pcm = malloc(total_bytes);
    if (!pcm) { fprintf(stderr, "oom\n"); return 3; }
    for (size_t f = 0; f < total_frames; f++)
        pcm[f] = (int16_t)(amp * 32767.0 *
                           sin(2.0 * M_PI * 997.0 * (double)f / 48000.0));

    size_t written = 0;
    double next_feed = now_s();
    double next_lat = now_s() + 1.0 / (latency_hz > 0 ? latency_hz : 5.0);
    double hold_at = now_s() + (hold_ms / 1000.0);
    double feed_deadline = now_s() + 6.0;
    int fired = 0;
    long lat_samples = 0;

    while (!stop_now && now_s() < feed_deadline) {
        double t = now_s();
        if (feed_ms > 0.0 && t < next_feed) {
            tick();
            continue;
        }
        size_t chunk_frames = (chunk_ms > 0.0)
            ? (size_t)(48000 * chunk_ms / 1000.0) : total_frames;
        size_t left = total_frames - written;
        if (left > 0) {
            size_t take = (chunk_frames < left) ? chunk_frames : left;
            size_t avail = pa_stream_writable_size(st);
            size_t bytes = take * 2;
            if (avail >= bytes) {
                if (pa_stream_write(st, pcm + written * 1, bytes, NULL, 0,
                                    PA_SEEK_RELATIVE) < 0) {
                    ev("write error=%s", pa_strerror(pa_context_errno(pa_stream_get_context(st))));
                    break;
                }
                written += take;
                ev("write frames=%zu total=%zu", take, written);
                if (feed_ms > 0.0)
                    next_feed = now_s() + feed_ms / 1000.0;
            }
        }
        /* NB: a completed single-shot feed does NOT end the leg — the
         * hold (uncork/trigger) and the monitor-capture window still
         * need the stream alive. The loop exits on `written && fired`
         * below or at the feed deadline. */
        if (now_s() >= next_lat) {
            sample_latency("mid");
            lat_samples++;
            next_lat = now_s() +
                1.0 / (latency_hz > 0 ? latency_hz : 5.0);
        }
        if (!fired && now_s() >= hold_at) {
            fired = 1;
            if (!strcmp(mode, "trigger")) {
                pa_operation *op = pa_stream_trigger(st, NULL, NULL);
                if (op) pa_operation_unref(op);
                ev("trigger");
            } else {
                pa_operation *op = pa_stream_cork(st, 0, NULL, NULL);
                if (op) pa_operation_unref(op);
                ev("uncork");
            }
        }
        if (written >= total_frames && fired)
            break;
        tick();
    }
    /* hold the stream open long enough for the monitor capture to see
     * the post-uncork tail, then stop */
    double tail_deadline = now_s() + 1.6;
    while (now_s() < tail_deadline && !stop_now) {
        if (now_s() >= next_lat) {
            sample_latency("mid");
            lat_samples++;
            next_lat = now_s() + 1.0 / (latency_hz > 0 ? latency_hz : 5.0);
        }
        tick();
    }
    sample_latency("final");
    ev("fed frames=%zu fired=%d lat_samples=%ld", written, fired,
       lat_samples);
    printf("SUMMARY mode=%s rc=0 fed=%zu fired=%d lat_samples=%ld\n",
           mode, written, fired, lat_samples);
    fflush(stdout);

done:
    if (st)
        pa_stream_disconnect(st);
    if (ctx)
        pa_context_disconnect(ctx);
    if (m)
        pa_mainloop_free(m);
    return 0;
}
