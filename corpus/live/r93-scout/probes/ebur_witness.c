/* r93 scout — host libebur128 witness (installed 1.2.6).
 * Answers, with return codes, the exact library semantics the plugin relies on:
 *  - which single-mode inits succeed (M/S/I/LRA/SAMPLE_PEAK/TRUE_PEAK/0)
 *  - ebur128_set_max_window units: set(2) then query(2|400|2000)
 *  - sample_peak/true_peak with channel_number >= channels (does *out change?)
 *  - set_channel with DUAL_MONO / index on a 1-channel state
 * Bounded: fixed-size program, no audio, no I/O beyond stdout.
 */
#include <ebur128.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

static double qwin(ebur128_state *st, unsigned long w) {
    double v = -12345.0;
    int rc = ebur128_loudness_window(st, w, &v);
    printf("    loudness_window(%lu ms) rc=%d out=%.6f\n", w, rc, v);
    return v;
}

int main(void) {
    int maj, min, pat;
    ebur128_get_version(&maj, &min, &pat);
    printf("libebur128 version %d.%d.%d\n", maj, min, pat);

    int modes[] = {EBUR128_MODE_M, EBUR128_MODE_S, EBUR128_MODE_I,
                   EBUR128_MODE_LRA, EBUR128_MODE_SAMPLE_PEAK,
                   EBUR128_MODE_TRUE_PEAK, 0,
                   EBUR128_MODE_M | EBUR128_MODE_I,
                   EBUR128_MODE_I | EBUR128_MODE_LRA};
    const char *names[] = {"M", "S", "I", "LRA", "SAMPLE_PEAK", "TRUE_PEAK", "0",
                           "M|I", "I|LRA"};
    for (int i = 0; i < 9; i++) {
        ebur128_state *st = ebur128_init(1, 48000, modes[i]);
        printf("init(mode=%s) -> %s\n", names[i], st ? "OK" : "NULL");
        if (st) ebur128_destroy(&st);
    }

    /* window units + clamping */
    ebur128_state *st = ebur128_init(1, 48000, EBUR128_MODE_M);
    printf("init(M) window defaults:\n");
    qwin(st, 0);
    qwin(st, 400);
    qwin(st, 2000);
    int rc = ebur128_set_max_window(st, 2);
    printf("  set_max_window(2) rc=%d\n", rc);
    qwin(st, 2);
    qwin(st, 400);
    qwin(st, 2000);
    rc = ebur128_set_max_window(st, 2000);
    printf("  set_max_window(2000) rc=%d\n", rc);
    qwin(st, 400);
    qwin(st, 2000);
    ebur128_destroy(&st);

    /* S-mode default window */
    st = ebur128_init(1, 48000, EBUR128_MODE_S);
    printf("init(S):\n");
    qwin(st, 3000);
    qwin(st, 400);
    ebur128_destroy(&st);

    /* setter unit discriminator: after set_max_window(500), a 100000 ms query
     * is legal iff the setter stores seconds (buffer 500 s), illegal iff ms. */
    st = ebur128_init(1, 48000, EBUR128_MODE_M);
    rc = ebur128_set_max_window(st, 500);
    printf("unit probe: set_max_window(500) rc=%d\n", rc);
    qwin(st, 500);
    qwin(st, 100000);
    ebur128_destroy(&st);

    /* peaks on a 1-channel state */
    st = ebur128_init(1, 48000, EBUR128_MODE_SAMPLE_PEAK | EBUR128_MODE_TRUE_PEAK | EBUR128_MODE_M);
    float buf[480] = {0};
    for (int i = 0; i < 480; i++) buf[i] = 0.5f * sinf(2 * 3.14159265358979f * 1000 * i / 48000.0f);
    for (int k = 0; k < 10; k++) ebur128_add_frames_float(st, buf, 480);
    for (int ch = 0; ch < 7; ch++) {
        double v = -777.0;
        int r1 = ebur128_sample_peak(st, (unsigned) ch, &v);
        double v2 = -777.0;
        int r2 = ebur128_true_peak(st, (unsigned) ch, &v2);
        printf("sample_peak(ch=%d) rc=%d out=%.6f | true_peak rc=%d out=%.6f\n",
               ch, r1, v, r2, v2);
    }
    ebur128_destroy(&st);

    /* set_channel on 1-channel state */
    st = ebur128_init(1, 48000, EBUR128_MODE_M);
    int r1 = ebur128_set_channel(st, 0, EBUR128_DUAL_MONO);
    int r2 = ebur128_set_channel(st, 6, EBUR128_DUAL_MONO);
    int r3 = ebur128_set_channel(st, 1, EBUR128_LEFT_SURROUND);
    printf("set_channel(0,DUAL_MONO) rc=%d ; (6,DUAL_MONO) rc=%d ; (1,SL) rc=%d\n", r1, r2, r3);
    /* feed a 0.5 amp sine; momentary/global with the map left as-is (LEFT) */
    float *big = malloc(sizeof(float) * 48000 * 2);
    for (int i = 0; i < 96000; i++) big[i] = 0.5f * sinf(2 * 3.14159265358979f * 1000 * i / 48000.0f);
    ebur128_add_frames_float(st, big, 96000);
    double m = 0, g = 0;
    ebur128_loudness_momentary(st, &m);
    ebur128_loudness_global(st, &g);
    printf("after sine: momentary=%.6f global=%.6f\n", m, g);
    free(big);
    ebur128_destroy(&st);
    return 0;
}
