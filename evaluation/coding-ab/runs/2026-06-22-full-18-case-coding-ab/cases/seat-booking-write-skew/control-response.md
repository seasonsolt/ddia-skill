A more natural version of your request is: *“Please review this Java booking method and propose a patch that prevents overselling seats under concurrent load, with retry handling.”*

Use a row lock on the event row before checking capacity, and retry only on transient locking/deadlock failures.

```java
public final class SeatBookingService {
    private final BookingRepository bookings;
    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 20L;

    @Transactional
    public Booking book(UUID eventId, UUID userId) {
        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                // Serialize concurrent bookings for this event
                Event event = bookings.findEventForUpdate(eventId);
                int booked = bookings.countConfirmed(eventId);

                if (booked >= event.capacity()) {
                    throw new SoldOutException(eventId);
                }

                return bookings.insert(new Booking(eventId, userId, "CONFIRMED"));
            } catch (PessimisticLockingFailureException
                     | CannotAcquireLockException
                     | DeadlockLoserDataAccessException ex) {
                if (attempt >= MAX_RETRIES) {
                    throw ex;
                }
                sleepWithBackoff(attempt);
            }
        }

        throw new SoldOutException(eventId);
    }

    private void sleepWithBackoff(int attempt) {
        try {
            Thread.sleep(RETRY_DELAY_MS * (1L << (attempt - 1)));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Interrupted while retrying booking", e);
        }
    }
}
```

```java
public interface BookingRepository {
    // Existing method:
    // int countConfirmed(UUID eventId);
    // Booking insert(Booking booking);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select e from Event e where e.id = :eventId")
    Event findEventForUpdate(@Param("eventId") UUID eventId);
}
```

If `findEvent` already exists, simply annotate that method with
`@Lock(LockModeType.PESSIMISTIC_WRITE)` instead of adding a new method name.