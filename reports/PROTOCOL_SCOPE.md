# Protocol and standards scope

- SUMO/TraCI: traffic simulator and its control interface. Lane permissions establish the implemented road-closure state. TraCI is an experiment-control interface, not a V2X over-the-air protocol.
- SEE-V2X: recorded C-V2X sidelink measurements. Current analyzed subset is a one-transmitter stationary parking-lot parameter sweep; application TX/RX logs support matched delivery and delay calculations. The source also provides MAC/SCI traces and outdoor intersection application runs, but these are not yet integrated into the benchmark.
- Semi-persistent scheduling (SPS): the current source configurations are marked sps, with 20 ms generation interval and reservation period. The benchmark consumes recorded outcomes; it does not implement or validate an SPS scheduler or the radio physical layer.
- 3GPP TR 37.885: methodology context for LTE/NR V2X evaluation, not a conformance certificate. No NR sidelink, 5G or 6G implementation or validation is claimed.
- Application: custom structured advisory with road/action, claim, timestamps and evidence version. It is not encoded as SAE J2735 BSM or ETSI CAM/DENM, and standardized message interoperability is not tested. SEE-V2X's BSM/perception workloads are source-data categories, not a claim about this advisory's encoding.
- Inference: localhost HTTP to Ollama and HTTPS to Nebius are separate application transports. Nebius client elapsed time already includes the provider Internet path; do not add that path again. Neither is measured mobile-operator Uu performance.
- Security: content consistency and freshness checks do not implement certificate authentication, message signing or a vehicular PKI. Unsupported claims and stale decisions are the present threat scope.

Primary sources checked 30 October 2026:
https://cisl.ucr.edu/SEE-V2X/
https://github.com/UCR-CISL/SEE-V2X
https://sumo.dlr.de/docs/TraCI/Change_Lane_State.html
https://sumo.dlr.de/docs/TraCI/Change_GUI_State.html
Existing manuscript reference tr37885 supplies the technical report.
