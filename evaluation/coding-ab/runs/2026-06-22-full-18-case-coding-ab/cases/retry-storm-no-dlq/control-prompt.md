You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

An email worker reads jobs from a queue, sends each message, and acknowledges the queue item afterward. During an outage, operators saw repeated sends for some users and one malformed job kept cycling through workers.

## Java Code

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
