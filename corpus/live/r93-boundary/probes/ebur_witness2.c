/* r93-boundary — independent witness: the INSTALLED libebur128's own integrated
 * loudness on a captured WAV, so the plugin-vs-own-reference "Global offset"
 * (r93-scout claim 16) can be attributed to the plugin, to the library, or to
 * the scout's Python reference.
 *
 * Usage: ebur_witness2 <wav> [full|trim] [rate_override]
 *   full : add every frame (leading/trailing silence included)
 *   trim : start at the first |x| > 0.001 and end at the last one
 * Prints one line per mode: frames, and ebur128_loudness_global.
 * Bounded: single file, no threads, no network. Links -lebur128 -lm.
 */
#include <ebur128.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned int rd32(const unsigned char *b) {
    return (unsigned)b[0] | ((unsigned)b[1] << 8) | ((unsigned)b[2] << 16) | ((unsigned)b[3] << 24);
}
static unsigned short rd16(const unsigned char *b) {
    return (unsigned short)((unsigned)b[0] | ((unsigned)b[1] << 8));
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s <wav> [full|trim]\n", argv[0]); return 2; }
    const char *mode = argc > 2 ? argv[2] : "full";
    FILE *f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "open failed\n"); return 1; }
    unsigned char hdr[12];
    if (fread(hdr, 1, 12, f) != 12 || memcmp(hdr, "RIFF", 4) || memcmp(hdr + 8, "WAVE", 4)) {
        fprintf(stderr, "not RIFF/WAVE\n"); return 1;
    }
    unsigned short tag = 0, bits = 0, nch = 0;
    unsigned int srate = 0;
    unsigned char *data = NULL;
    unsigned int dlen = 0;
    for (;;) {
        unsigned char cid[4], szb[4];
        if (fread(cid, 1, 4, f) != 4 || fread(szb, 1, 4, f) != 4) break;
        unsigned int csz = rd32(szb);
        if (!memcmp(cid, "fmt ", 4)) {
            unsigned char b[40];
            unsigned int n = csz < 40 ? csz : 40;
            if (fread(b, 1, n, f) != n) break;
            tag = rd16(b); nch = rd16(b + 2); srate = rd32(b + 4); bits = rd16(b + 14);
            if (csz > n) fseek(f, (long)(csz - n), SEEK_CUR);
        } else if (!memcmp(cid, "data", 4)) {
            data = (unsigned char *)malloc(csz);
            if (!data) { fprintf(stderr, "oom\n"); return 1; }
            dlen = (unsigned int)fread(data, 1, csz, f);
            break;
        } else {
            fseek(f, (long)csz, SEEK_CUR);
        }
    }
    fclose(f);
    if (!data) { fprintf(stderr, "no data chunk\n"); return 1; }

    unsigned int bytes = bits / 8;
    unsigned int nframes = dlen / (bytes * (nch ? nch : 1));
    float *x = (float *)malloc(sizeof(float) * (size_t)nframes * nch);
    if (!x) { fprintf(stderr, "oom\n"); return 1; }
    for (unsigned int i = 0; i < (unsigned int)nframes * nch; i++) {
        if (tag == 3 && bits == 32) {
            float v; memcpy(&v, data + (size_t)i * 4, 4); x[i] = v;
        } else if (tag == 1 && bits == 16) {
            short v; memcpy(&v, data + (size_t)i * 2, 2); x[i] = v / 32768.0f;
        } else if (tag == 1 && bits == 32) {
            int v; memcpy(&v, data + (size_t)i * 4, 4); x[i] = v / 2147483648.0f;
        } else { fprintf(stderr, "unsupported tag=%u bits=%u\n", tag, bits); return 1; }
    }
    free(data);

    unsigned int start = 0, end = nframes;
    if (!strcmp(mode, "trim")) {
        while (start < nframes) {
            float m = 0;
            for (unsigned int c = 0; c < nch; c++) { float a = fabsf(x[(size_t)start * nch + c]); if (a > m) m = a; }
            if (m > 0.001f) break;
            start++;
        }
        while (end > start) {
            float m = 0;
            for (unsigned int c = 0; c < nch; c++) { float a = fabsf(x[(size_t)(end - 1) * nch + c]); if (a > m) m = a; }
            if (m > 0.001f) break;
            end--;
        }
    }
    ebur128_state *st = ebur128_init(nch, srate, EBUR128_MODE_I);
    if (!st) { fprintf(stderr, "init failed\n"); return 1; }
    size_t add = end - start;
    int rc = ebur128_add_frames_float(st, x + (size_t)start * nch, add);
    double g = -999.0;
    int grc = ebur128_loudness_global(st, &g);
    printf("file=%s mode=%s ch=%u rate=%u tag=%u bits=%u nframes=%u used=%zu add_rc=%d global_rc=%d I=%.6f\n",
           argv[1], mode, nch, srate, tag, bits, nframes, add, rc, grc, g);
    ebur128_destroy(&st);
    free(x);
    return 0;
}
