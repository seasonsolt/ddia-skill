# DDIA Reading Ledger

Original notes extracted from line-by-line reading of the local DDIA PDF.
Do not paste long source passages into this file.

## Chapter 1. Reliable, Scalable, and Maintainable Applications

Start page: 25

Reviewed: yes

### Target engineering decisions
- Decide which faults the system must absorb and which risks should be prevented outright.
- Choose load parameters that actually explain bottlenecks, such as fan-out, write rate, read rate, data size, or cache hit rate.
- Define performance goals with percentiles, not averages, especially for user-facing paths.
- Decide when to scale vertically, horizontally, elastically, or manually based on workload predictability and operational complexity.

### Failure modes
- A local component fault becomes a user-visible outage because no isolation or fallback exists.
- Correlated software bugs crash many nodes at once when rare inputs or environmental assumptions appear.
- Human configuration mistakes cause outages because production changes are too easy to apply broadly.
- Tail latency compounds across backend calls and makes whole user requests slow.

### Trade-offs
- Hardware redundancy is simpler than distributed software recovery, but it may not handle whole-machine or cloud-instance loss.
- Write-time fan-out improves read latency but creates bursty write amplification for high-follower or high-cardinality entities.
- Elastic scaling handles unpredictable traffic, but manual capacity planning is easier to reason about.
- Restrictive operational interfaces reduce mistakes, but too much friction causes people to bypass them.

### Review questions
- What concrete faults does this design tolerate, and how has each path been tested?
- Which load parameters would double first, and what part of the architecture would fail first?
- Are dashboards showing client-visible latency percentiles and error rates, not just server averages?
- Can operators roll back config, drain nodes, restore data, and diagnose dependency problems quickly?

### Skill guidance
- Treat application composition of databases, caches, queues, and indexes as data-system design, not glue code.
- Design observability and recovery paths before assuming failures will be rare.
- Use chaos-style fault injection only where recovery behavior is well bounded and measurable.
- Keep abstractions small enough that new engineers can predict behavior during incidents and changes.

## Chapter 2. Data Models and Query Languages

Start page: 49

Reviewed: yes

### Target engineering decisions
- Choose document, relational, or graph modeling based on relationship shape, not database fashion.
- Use document storage when data is usually consumed as a bounded tree and cross-document relationships are rare.
- Use relational modeling when joins, normalization, and flexible query evolution matter.
- Use graph modeling when relationships are numerous, variable, and central to product behavior.

### Failure modes
- A document model becomes painful after features introduce many-to-many relationships.
- Denormalized fields drift apart because application code owns consistency across copies.
- Schemaless data still has an implicit schema, but validation failures move into runtime code.
- Application-side joins create extra network round trips and inconsistent query behavior.

### Trade-offs
- Normalization reduces update anomalies but may require joins and more schema design.
- Denormalization improves locality and read convenience but increases write complexity.
- Schema-on-write catches bad data early, while schema-on-read is more flexible for heterogeneous records.
- Declarative query languages reduce application logic and enable optimizer improvements, but expose less procedural control.

### Review questions
- Are the main entities mostly trees, tables with joins, or networks of relationships?
- Which fields are duplicated, and what process keeps every copy correct?
- How will old and new record shapes coexist during schema evolution?
- Does the query language express the business question directly, or does application code manually navigate access paths?

### Skill guidance
- Model IDs for values that may be renamed, localized, searched hierarchically, or shared across records.
- Expect relationships to grow over time; avoid designs that only work for the first feature set.
- Prefer declarative queries when the database can optimize execution better than application code.
- Use graph query languages for variable-depth traversal instead of forcing recursive relationship logic into ordinary SQL unless the complexity is acceptable.

## Chapter 3. Storage and Retrieval

Start page: 91

Reviewed: yes

### Target engineering decisions
- Select storage engines by access pattern: low-latency keyed operations versus large analytical scans.
- Add indexes only for query paths that justify their write and storage overhead.
- Choose B-tree-oriented systems when predictable reads, range locking, and mature transactional behavior dominate.
- Choose LSM-oriented systems when high write throughput and sequential disk writes are more important.

### Failure modes
- Too many indexes slow writes and increase storage without improving critical queries.
- LSM compaction falls behind, causing disk growth, read slowdown, and high-percentile latency spikes.
- In-memory indexes or key maps exceed RAM and turn a fast design into an unstable one.
- Analytical queries run against OLTP systems and degrade customer-facing transaction latency.

### Trade-offs
- Append-only logs simplify writes and recovery but require compaction and deletion markers.
- B-trees give stable lookup behavior but pay for in-place page updates, WAL writes, and page splits.
- Clustered and covering indexes speed selected reads but duplicate data and complicate writes.
- Columnar storage accelerates analytical scans but makes frequent small writes and row reconstruction less natural.

### Review questions
- Is the workload dominated by point lookups, range scans, full-text search, geospatial filters, or large aggregations?
- What is the write amplification from indexes, WALs, compaction, materialized views, and replication?
- Can compaction, cache misses, or checkpointing explain p99 latency under production load?
- Should analytics be isolated through a warehouse, ETL pipeline, or columnar store instead of hitting OLTP tables?

### Skill guidance
- Treat indexes as derived structures with operational cost, not free performance switches.
- Benchmark storage engines with the real read/write mix, key cardinality, value sizes, and latency targets.
- Monitor LSM segment growth, compaction backlog, disk bandwidth, and read amplification explicitly.
- Preserve raw analytical data where possible, and use materialized aggregates only for known expensive query patterns.

## Chapter 4. Encoding and Evolution

Start page: 133

Reviewed: yes

### Target engineering decisions
- Choose encodings that support rolling deploys with old and new code running together.
- Avoid language-native serialization for durable storage or cross-service APIs.
- Use schema-driven binary formats when compactness, typed contracts, and evolution rules matter.
- Pick REST for public/debuggable APIs and RPC for controlled internal paths where generated clients are acceptable.

### Failure modes
- Reusing field tags or making new fields mandatory can make historical data unreadable.
- Old services may drop unknown fields when reading, updating, and writing records back.
- RPC clients may treat network calls like local calls and mishandle timeout, retry, and duplication.
- JSON number, binary, and schema ambiguity can corrupt data across language boundaries.

### Trade-offs
- Text formats are easy to inspect and integrate, but weaker on type precision and size.
- Thrift/Protobuf give compact messages, but require stable tag discipline and schema tooling.
- Avro fits dynamic schemas and data files well, but readers must obtain the writer schema.
- Message brokers decouple sender and receiver, but make replies, ordering, and schema preservation explicit design work.

### Review questions
- Can old code safely ignore every field the new code may write?
- Do update paths preserve unknown fields through decode, business logic, and re-encode?
- Does the API versioning plan support clients that cannot upgrade on your schedule?
- Are retry semantics, idempotency keys, and timeout behavior documented for every remote write?

### Skill guidance
- Treat stored data as a message to future versions of your application.
- Reserve schema field identifiers permanently once data may exist in the wild.
- Add fields as optional or defaulted, then enforce requirements at the application boundary if needed.
- Test compatibility with mixed-version services before relying on rolling deployment.

## Chapter 5. Replication

Start page: 173

Reviewed: yes

### Target engineering decisions
- Decide whether each workload needs single-leader, multi-leader, or leaderless replication.
- Choose synchronous, semi-synchronous, or asynchronous replication based on durability and latency requirements.
- Define read guarantees explicitly: read-your-writes, monotonic reads, consistent-prefix reads, or eventual consistency.
- Set quorum parameters from failure tolerance and stale-read tolerance, not from defaults alone.

### Failure modes
- Asynchronous failover can lose acknowledged writes when a lagging follower becomes leader.
- Split brain can corrupt data if two leaders accept writes without fencing or conflict handling.
- Replica lag can make users miss their own writes, see time move backward, or observe causally impossible states.
- Last-write-wins conflict handling can silently discard successful concurrent writes.

### Trade-offs
- Single-leader replication is simpler, but all writes depend on one leader path.
- Multi-leader replication lowers cross-region write latency, but pushes conflict resolution into the design.
- Leaderless replication improves availability under node loss, but weakens consistency and complicates conflict detection.
- Sloppy quorums raise write availability, but remove the normal quorum overlap guarantee until hinted handoff completes.

### Review questions
- What happens to acknowledged writes if the current leader dies before followers receive them?
- Which reads must go to the leader or a sufficiently fresh replica after a user writes?
- How does the system detect and resolve concurrent writes without losing business intent?
- Are replica lag, stale reads, failed handoffs, and anti-entropy progress visible in monitoring?

### Skill guidance
- Design failover as a data-safety path, not only an availability path.
- Route user-sensitive reads using session metadata, write timestamps, or leader reads where needed.
- Prefer explicit merge semantics or CRDT-like structures when concurrent writes are normal.
- Load-test replication under lag, node outage, leader promotion, and cross-datacenter interruption.

## Chapter 6. Partitioning

Start page: 221

Reviewed: yes

### Target engineering decisions
- Choose key-range partitioning when range scans matter more than uniform write distribution.
- Choose hash partitioning when balanced load matters more than primary-key range queries.
- Decide whether secondary indexes should be local to documents or globally partitioned by term.
- Pick a rebalancing strategy that matches expected data growth, node churn, and operational control.

### Failure modes
- Sequential or timestamp-leading keys can concentrate all current writes on one hot partition.
- Hashing does not fix a single extremely hot key; the application may need key splitting.
- Scatter/gather secondary-index queries can amplify tail latency across many partitions.
- Automatic rebalancing can worsen overload if failure detection mistakes a slow node for a dead node.

### Trade-offs
- Key-range partitions preserve ordering, but require careful boundary management and hot-spot avoidance.
- Hash partitions distribute keys well, but make range queries expensive or impossible.
- Local secondary indexes make writes cheap, but reads may need every partition.
- Global secondary indexes make reads targeted, but writes touch multiple partitions and may update asynchronously.

### Review questions
- Does the partition key match the dominant read and write access patterns?
- Which keys can become hot because of celebrities, tenants, time windows, or shared counters?
- During rebalancing, can the system keep serving reads and writes without moving unnecessary data?
- How do clients, routing tiers, or nodes learn the current partition-to-node mapping?

### Skill guidance
- Model partition choice from real access patterns, not only data volume.
- Add synthetic spreading only for known hot keys, and budget for fan-in reads afterward.
- Keep partition metadata authoritative through a coordination service, routing tier, or well-tested gossip mechanism.
- Treat multi-partition writes as a separate consistency problem that needs transaction or compensation design.

## Chapter 7. Transactions

Start page: 243

Reviewed: yes

### Target engineering decisions
- Choose isolation level by invariant risk, not by database default.
- Use multi-object transactions when one user action must update several records atomically.
- Prefer database constraints for simple invariants such as uniqueness and foreign-key validity.
- Use serializable isolation for workflows where decisions depend on predicates over changing data.

### Failure modes
- Read-modify-write logic can silently lose concurrent updates.
- Snapshot isolation can still allow write skew when transactions update different rows.
- Predicate checks can be invalidated by newly inserted matching rows.
- Retrying aborted transactions can duplicate external side effects unless those effects are idempotent.

### Trade-offs
- Read committed is fast and common but leaves many race conditions to application code.
- Snapshot isolation gives stable reads but does not guarantee all invariants.
- Two-phase locking provides strong isolation but can hurt latency and throughput under contention.
- Serializable snapshot isolation improves concurrency but requires abort handling and retry design.

### Review questions
- Which business invariants must remain true under concurrent requests?
- Are all read-modify-write paths protected by atomic operations, locks, or conflict detection?
- Can any query-then-insert or query-then-update workflow suffer from phantom conflicts?
- Are transaction retries safe with emails, payments, queues, caches, and other external systems?

### Skill guidance
- Treat weak isolation as an API contract that must be tested with adversarial concurrency cases.
- Model each critical workflow as reads, decisions, and writes before choosing isolation.
- Push simple invariants into database constraints instead of relying only on service code.
- Add explicit retry, backoff, and idempotency handling wherever transactions may abort.

## Chapter 8. The Trouble with Distributed Systems

Start page: 295

Reviewed: yes

### Target engineering decisions
- Design remote calls as uncertain outcomes, not as reliable function calls.
- Set timeouts from measured latency distributions and failure impact, not guesswork.
- Use monotonic clocks for elapsed time and wall clocks only when real timestamps are required.
- Require quorum or coordination protocols for decisions that cannot safely be made by one node.

### Failure modes
- A missing response does not reveal whether the request failed, succeeded, or is delayed.
- Clock drift, clock jumps, and bad synchronization can corrupt timestamp-based ordering.
- Long process pauses can make a live node look dead and then reappear with stale assumptions.
- A degraded node can keep accepting work while being too slow to meet protocol expectations.

### Trade-offs
- Short timeouts detect problems faster but increase false failovers during delay spikes.
- Hard real-time guarantees are possible only with expensive constraints and lower utilization.
- Commodity distributed systems gain cost efficiency but must tolerate partial failures constantly.
- Fencing tokens add protocol complexity but protect shared resources from stale lock holders.

### Review questions
- What happens if a request succeeds but the response is lost?
- Which components rely on synchronized wall clocks for correctness rather than observability?
- Can a paused process resume and still perform writes using an expired lease?
- Does every external resource validate ownership with a monotonically increasing token or equivalent guard?

### Skill guidance
- Assume networks delay, drop, duplicate, and reorder communication at inconvenient moments.
- Separate failure detection from correctness; suspicion alone should not authorize unsafe action.
- Record enough metadata to make retries, deduplication, and reconciliation explicit.
- Test under injected latency, packet loss, clock skew, process pauses, and partial degradation.

## Chapter 9. Consistency and Consensus

Start page: 343

Reviewed: yes

### Target engineering decisions
- Use linearizability only for state that needs a single current truth.
- Prefer causal or eventual models when branching histories and reconciliation are acceptable.
- Use proven consensus systems for leader election, membership, locks, and coordination.
- Keep consensus-managed data small, critical, and operationally simple.

### Failure modes
- Leader-based systems stop making safe progress when leadership is ambiguous.
- Last-write-wins can discard valid concurrent work while appearing successful.
- Distributed commit can block while participants hold locks and wait for a failed coordinator.
- Service discovery or lock services can cause split-brain behavior if clients act on stale membership.

### Trade-offs
- Linearizability is easy to reason about but adds coordination latency.
- Causal consistency scales better but cannot decide uniqueness or exclusive ownership alone.
- Two-phase commit gives atomic distributed outcomes but has blocking and recovery burdens.
- Consensus improves automated failover but needs majorities, stable membership handling, and careful operations.

### Review questions
- Which operations truly require linearizable reads or writes?
- Can uniqueness, locking, leader election, or membership be reduced to an existing consensus service?
- What is the recovery path if a transaction coordinator dies after participants prepare?
- Does the system keep serving safely when a leader is unreachable but not certainly dead?

### Skill guidance
- Do not build custom consensus protocols for production coordination.
- Treat total ordering, compare-and-set, distributed commit, and leader election as related coordination problems.
- Use coordination services for metadata and decisions, not as general-purpose databases.
- Document where the system chooses availability over single-copy consistency and how conflicts are resolved.

## Chapter 10. Batch Processing

Start page: 411

Reviewed: yes

### Target engineering decisions
- Use batch jobs when inputs are bounded, replayable, and throughput matters more than user-facing latency.
- Prefer immutable inputs and replaceable outputs for derived data such as indexes, recommendations, reports, and serving snapshots.
- Choose reduce-side joins when input layout is unknown; choose map-side joins when size, partitioning, or sort order guarantees are available.
- Use higher-level dataflow APIs when query planning, join selection, and operational maintainability matter more than hand-written MapReduce control.

### Failure modes
- Hot keys can strand work on one reducer and delay the whole workflow.
- Remote per-record lookups can destroy throughput and overload OLTP systems.
- Writing directly from batch tasks into external databases can expose partial output and duplicate side effects.
- Nondeterministic operators make recomputation unsafe after task or node failure.

### Trade-offs
- Sorting scales beyond memory and favors sequential I/O, but can be slower than in-memory aggregation for small working sets.
- Materializing intermediate data improves recovery and reuse, but adds disk, replication, and scheduling cost.
- Dataflow engines reduce intermediate writes and startup overhead, but may need more recomputation after failures.
- Raw data lakes speed ingestion and experimentation, but shift schema interpretation burden to consumers.

### Review questions
- Is this job processing a bounded snapshot, or should it be modeled as a stream?
- Which datasets are immutable inputs, intermediate artifacts, and published outputs?
- Are join keys skewed, and do hot-key mitigation or pre-aggregation strategies exist?
- Can failed tasks be retried without external side effects or nondeterministic output?

### Skill guidance
- Design batch pipelines as deterministic transformations from input datasets to new output datasets.
- Keep network I/O out of per-record processing; colocate required data before the job runs.
- Publish outputs atomically by writing new files first, then switching readers to the new version.
- Treat partitioning, sort order, and file format as operational metadata required for safe optimization.

## Chapter 11. Stream Processing

Start page: 461

Reviewed: yes

### Target engineering decisions
- Use log-based brokers when replay, ordering, fan-out, and derived state maintenance are required.
- Use traditional queues for task distribution when per-message ordering and historical replay are not important.
- Model database writes as streams when keeping caches, search indexes, warehouses, and materialized views in sync.
- Choose event-time windows for analytics that must survive lag, replay, restarts, and historical backfills.

### Failure modes
- Consumer lag can exceed retention and silently lose required events.
- Redelivery after consumer failure can reorder messages under load-balanced queues.
- Dual writes can leave databases, caches, and indexes permanently inconsistent.
- Processing-time windows can create false spikes or gaps after backlog, restart, or replay.

### Trade-offs
- Durable logs support replay and isolation between consumers, but require retention planning and offset monitoring.
- Event sourcing improves auditability and evolution, but may need snapshots and careful handling of deletion requirements.
- Local stream state avoids remote lookups, but needs checkpointing, changelog replication, or rebuild plans.
- Exactly-once effects require transactions, idempotence, or deterministic replay, each with constraints and overhead.

### Review questions
- What is the source of truth: an OLTP database changelog, an application event log, or another stream?
- Are consumers allowed to replay old events, and how long must the log retain them?
- Are joins stream-stream, stream-table, or table-table, and what state must each retain?
- What happens to external side effects if a stream task crashes after producing output?

### Skill guidance
- Separate commands that may fail validation from immutable events that record accepted facts.
- Carry stable event IDs or offsets into sinks so repeated processing can be deduplicated.
- Record event timestamps carefully, especially when clients can buffer offline or have unreliable clocks.
- Monitor consumer lag, late events, dropped events, and state recovery time as first-class production signals.

## Chapter 12. The Future of Data Systems

Start page: 511

Reviewed: yes

### Target engineering decisions
- Compose specialized storage and processing systems by deriving views from a clear system of record.
- Prefer ordered logs, CDC, and idempotent consumers over heterogeneous distributed transactions for most integration work.
- Use batch reprocessing to evolve schemas, rebuild derived views, and recover from bad derivation code.
- Decide explicitly where correctness needs timeliness, and where asynchronous integrity checks are sufficient.

### Failure modes
- Multiple systems accepting writes independently can disagree on ordering and diverge permanently.
- Missing causal dependencies across partitions, services, or datacenters can produce incorrect derived actions.
- Blind trust in databases, disks, backups, or application code can hide corruption until repair is expensive.
- Predictive and tracking systems can create unfair outcomes, privacy loss, and hard-to-appeal automated decisions.

### Trade-offs
- Unbundled systems improve breadth and independent evolution, but add operational complexity and integration burden.
- Asynchronous logs contain failures better than distributed transactions, but usually weaken read-your-writes timing.
- Strict constraints require coordination; loose constraints can scale better if compensation is acceptable.
- Recording reads improves provenance and causal analysis, but increases storage, I/O, and privacy risk.

### Review questions
- Which system decides the canonical order of writes, and which systems are derived from it?
- Can every derived dataset be rebuilt from retained events, snapshots, and deterministic code?
- Which constraints must be enforced before acceptance, and which can be checked after the fact?
- What audits prove that derived state, backups, logs, and business invariants remain intact end to end?

### Skill guidance
- Treat indexes, caches, search stores, ML models, and analytics tables as derived state with documented lineage.
- Pass end-to-end operation IDs from clients through logs, processors, and sinks for duplicate suppression.
- Build audit jobs that recompute invariants and compare derived state against the source of record.
- Minimize personal data retention, design for deletion, and review data use for consent, harm, bias, and accountability.
