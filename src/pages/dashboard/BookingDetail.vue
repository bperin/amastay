<script setup lang="ts">
// ... existing imports ...

const bookingStore = useBookingStore();
const booking = ref<Booking | null>(null);

onMounted(async () => {
    const bookingId = props.id;
    if (bookingId) {
        try {
            booking.value = await bookingStore.getBooking(bookingId);
        } catch (error) {
            console.error('Error fetching booking:', error);
        }
    }
});
</script> 