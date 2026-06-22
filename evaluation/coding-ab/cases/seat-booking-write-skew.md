# Coding Case: seat-booking-write-skew

Case ID: seat-booking-write-skew
Category: bad
Language: Java
Primary DDIA topics: transactions, isolation, invariants, concurrency control

## Scenario

An event ticketing service confirms bookings by counting existing confirmed rows before inserting another booking. During popular releases, operators sometimes see more confirmed bookings than the event capacity.

## Flawed Java

```java
public final class SeatBookingService {
    private final BookingRepository bookings;

    @Transactional
    public Booking book(UUID eventId, UUID userId) {
        int booked = bookings.countConfirmed(eventId);
        Event event = bookings.findEvent(eventId);
        if (booked >= event.capacity()) {
            throw new SoldOutException(eventId);
        }
        return bookings.insert(new Booking(eventId, userId, "CONFIRMED"));
    }
}
```

## Task

Review the code and propose a patch that keeps confirmed bookings within capacity under concurrent requests and retries.

## Expected DDIA Reasoning

The answer should identify the count-then-insert check as vulnerable to write skew under concurrent transactions unless the capacity invariant is enforced durably. A strong patch should move the invariant into a database-enforced operation such as a locked event row, conditional capacity update, exclusion or uniqueness constraint over reservations, serializable isolation with retry, or a reservation table that makes capacity consumption explicit.

## Strong Patch Signals

- Uses a conditional capacity decrement or locks the event row before inserting the booking.
- Adds an idempotency key or request identifier so retries do not create duplicate confirmed bookings.
- Adds concurrent overbooking tests that prove capacity is not exceeded.

## Weak Patch Patterns

- Adds Java `synchronized`, which does not protect multiple service instances or direct database writers.
- Uses a Redis lock as the only correctness boundary instead of a durable invariant.
- Retries failed inserts without changing the invariant enforcement.

## Scoring Notes

- Award high scores for putting the capacity invariant in the storage layer and describing the required retry behavior.
- Penalize answers that only make the read more recent while leaving check-then-insert non-atomic.
