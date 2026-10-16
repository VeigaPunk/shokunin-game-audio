# R99 Missing-Witness Fold

Before: 25366585, source sha 72b23e04... . This fold changes missing-data
and unexpected-abort reporting, not RTP packet/DSP assertions or bands.
It does not run the physical-LAN control.

## Data Walk And Correction

The actual e2e LAN statement group has two nested preconditions: a
client must open and its sink must reach running. Neither failure path
previously recorded an unmeasured result. A missing default interface
also dropped both leg keys. The opt-in control had the same silent
preconditions and never marked an executed measurement true.

Production branches now use a small named-unmeasured recorder, preserve
both no-interface keys, and name the missing-client/unreached-node
causes. LAN/control dictionaries are attached before the observation
work so a later exception retains that partial dictionary. The control
sets measured:true only after obtaining its counter difference.
Measured does NOT mean its existing positive-control assertion passed.

All five private-entry exception handlers formerly appended only a
coverage block. Unexpected backend exceptions now append the same
reason to failures as well, retaining the existing finally teardown.
This is a fail-closed harness correction, not a claim that an
infrastructure exception refutes a network-transport law.

Closed scope: critic C2's LAN preconditions; reviewer F1/F2 and
simplifier F6; critic C8's measured-flag asymmetry. The native-block
wording concern C5/reviewer F4 was already corrected by the earlier
e302dbce fold; its current message no longer asserts the sink emitted.

## Evidence

- An AST-isolated test executes the actual LAN statement group and
  actual exception handlers, with all actor/tap/play/sleep operations
  replaced by inert callbacks. The original four tests produce eight
  failing subcases, then all four pass after the repair.
- One additional selected test executes the actual opt-in guard against
  a MOCK environment, ready-node callback and zero counter delta.
  It records measured:true while the unchanged control assertion
  refutes the zero result. No positive egress measurement is fabricated.
  This fifth test passes separately, not as a claimed combined rerun.
- The two existing no-network default-off guard tests pass on the
  changed source. No real process environment enables the LAN arm.
- Source/test compile and source diff checks pass.

Source sha:
9f242022408b7447cc9afeac44a34d353c37bd8b8cf60efa8e04c3bd780933ec.
Final test sha:
fdd527aa2f7493cfd7270e4f8d57183306504e7762c4d68c02fc58c1d38222a1.
Raw before/after, selected measured/refuted and gate outputs:
audio-final-guard-proof/r99-missing-*.{stdout,stderr,rc}.

No live family, multicast control or service operation is repeated.
Counter-None still aborts coarsely, now fail-closed with the early LAN
dictionary retained. An entry-header exception before the internal try
can still escape the end-of-run writer; this fold does not claim a
universal exception-custody boundary. The generic sink-leg missing-tap
finding still needs caller-specific disposition, not a blanket assumption
that all its callers silently pass.
