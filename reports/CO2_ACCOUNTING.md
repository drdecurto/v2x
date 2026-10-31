# CO2 accounting foundation

Six existing city/signal configurations rerun with explicit HBEFA3/PC_G_EU6, identical routes/seed4101/horizon2400s. This is a homogeneous gasoline Euro6 archetype, not local fleet calibration or physical measurement. Primary totals are tripinfo CO2_abs in mg, divided by1e6 for kg, including unfinished trips. Independent Decimal aggregation verifies every emitted vehicle ID.

Actuated/static kg: LA596.587293/661.804751; Luxembourg367.572034/434.961505; Pedralbes355.711479/457.900833. LA static unfinished8vehicles contribute34.848958kg.23Pedralbes exclusions remain explicit. Prior timing and route lengths match within prior output precision (unfinished route lengths rounded to0.01m). No safety outcome changes.

Original proposed exact per-step/trip reconciliation failed and is preserved. Native rates times0.5s give totals0.013826–0.163335% below trip-device sums. SUMO1.27.1 source uses movement notifications for trip-device accumulation and current vehicle state for emission export; this inspection does not establish a complete mathematical correction. Do not silently force equality, average conventions, or claim physical validation. Primary device totals are consistent across comparisons; rates remain diagnostics. Original plan, amendment and precision-check records retained.

Source: https://sumo.dlr.de/docs/Simulation/Output/EmissionOutput.html ; https://sumo.dlr.de/docs/Models/Emissions/HBEFA3-based.html ; https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/devices/MSDevice_Emissions.cpp ; https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/output/MSEmissionExport.cpp . Checked2026-10-30.

Prospective protocol: protocols/environmental_advisories_v1.md. Not frozen or preregistered; no environmental policy outcomes yet. Next implement city incident/advisory fixtures with common routing and driver compliance, preserving source/receiver/evaluation separation. Freeze models, messages, traces and power/analysis decisions before held-out execution.33existing tests pass. No new model calls.
