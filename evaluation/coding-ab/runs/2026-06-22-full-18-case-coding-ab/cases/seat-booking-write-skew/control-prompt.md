You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

An event ticketing service confirms bookings by counting existing confirmed rows before inserting another booking. During popular releases, operators sometimes see more confirmed bookings than the event capacity.

## Java Code

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
