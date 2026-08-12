# ASHREL configuration reference

ASHREL is the Ashfall field-telemetry relay daemon. This reference
lists every supported key with its shipped default as of v0.9.
Where the changelog records a later change, the changelog is
authoritative.

## auth.rate

Default: `240/min`.
Controls the rate side of `auth`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## filter.quota

Default: `1000`.
Controls the quota side of `filter`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## auth.mode

Default: `manual`.
Controls the mode side of `auth`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## filter.window

Default: `5s`.
Controls the window side of `filter`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## cache.ttl

Default: `120s`.
Controls the ttl side of `cache`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## beacon.quota

Default: `1000`.
Controls the quota side of `beacon`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## retry.ttl

Default: `120s`.
Controls the ttl side of `retry`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## filter.timeout

Default: `45s`.
Controls the timeout side of `filter`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## relay.ttl

Default: `120s`.
Controls the ttl side of `relay`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## beacon.ttl

Default: `30s`.
Controls the ttl side of `beacon`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## relay.rate

Default: `30/min`.
Controls the rate side of `relay`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## probe.ttl

Default: `10s`.
Controls the ttl side of `probe`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## filter.threshold

Default: `75%`.
Controls the threshold side of `filter`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## beacon.interval

Default: `15s`.
Controls the interval side of `beacon`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## cache.mode

Default: `strict`.
Controls the mode side of `cache`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## relay.depth

Default: `32`.
Controls the depth side of `relay`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## batch.window

Default: `45s`.
Controls the window side of `batch`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## uplink.mode

Default: `strict`.
Controls the mode side of `uplink`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## retry.timeout

Default: `20s`.
Controls the timeout side of `retry`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## spool.limit

Default: `1000`.
Controls the limit side of `spool`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## beacon.rate

Default: `120/min`.
Controls the rate side of `beacon`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## ingest.limit

Default: `128`.
Controls the limit side of `ingest`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## probe.mode

Default: `strict`.
Controls the mode side of `probe`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

Operational note: field crews should prefer the default unless a mast-specific survey says otherwise. Every override must be recorded in the ops log with the operator's callsign and the date, or the nightly audit flags the mast as unmanaged.

## ingest.interval

Default: `120s`.
Controls the interval side of `ingest`. Set too aggressively this
starves the spool; too lax and the uplink queue grows.

## Appendix: deployment checklist

1. night shift handover, all channels nominal.
2. recalibrated the barometer against the reference unit.
3. routine sweep of the west mast; nothing to report.
4. routine sweep of the west mast; nothing to report.
5. vendor ticket still open, no response this week.
6. night shift handover, all channels nominal.
7. night shift handover, all channels nominal.
8. generator test run completed, fuel at 61 percent.
9. night shift handover, all channels nominal.
10. reseated the uplink patch cable after intermittent CRC noise.
11. generator test run completed, fuel at 61 percent.
12. vendor ticket still open, no response this week.
13. generator test run completed, fuel at 61 percent.
14. archived last month's raw frames to cold spool.
