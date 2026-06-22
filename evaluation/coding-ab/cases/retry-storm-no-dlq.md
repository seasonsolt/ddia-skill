# Coding Case: retry-storm-no-dlq

Case ID: retry-storm-no-dlq
Category: bad
Language: Java
Primary DDIA topics: retries, queues, idempotency, fault tolerance

## Scenario

An email worker reads jobs from a queue, sends each message, and acknowledges the queue item afterward. During an outage, operators saw repeated sends for some users and one malformed job kept cycling through workers.

## Flawed Java

```java
public final class EmailWorker {
    private final QueueClient queue;
    private final EmailSender sender;

    public void handle(Message message) {
        EmailJob job = EmailJob.fromJson(message.body());
        sender.send(job.to(), job.subject(), job.body());
        queue.ack(message.id());
    }
}
```

## Task

Review the worker and propose a patch that handles send failures, acknowledgement failures, and malformed or permanently failing jobs.

## Expected DDIA Reasoning

The answer should identify that a failure after `sender.send` and before `queue.ack` can duplicate email, while poison messages can retry forever. A strong patch should add idempotency keys for sends, bounded retries, a dead-letter path, visibility timeout handling, and metrics for retry and DLQ behavior.

## Strong Patch Signals

- Uses an idempotent send key or durable sent-record keyed by message or email job id.
- Tracks attempt count and moves exhausted or invalid messages to a DLQ.
- Handles visibility timeout and adds tests for duplicate sends and retry exhaustion.

## Weak Patch Patterns

- Catches all exceptions and acknowledges the message, losing unsent email.
- Retries forever without a dead-letter policy or operator-visible state.
- Adds sleep in the handler without backpressure, attempt limits, or queue-level controls.

## Scoring Notes

- Award high scores for separating transient failures from poison messages and making duplicates observable.
- Penalize answers that trade duplicate sends for silent data loss.
