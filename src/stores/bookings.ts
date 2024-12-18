import { defineStore } from 'pinia';
import { BookingsApi } from '@/generated/src/apis/BookingsApi';
import type { Booking } from '@/generated/src/models';
import { configuration } from '@/api';
import { ref } from 'vue';

export const useBookingStore = defineStore('bookings', () => {
    const api = new BookingsApi(configuration);
    const error = ref<string | null>(null);
    const bookings = ref<Booking[]>([]);

    const getBookingById = async (bookingId: string): Promise<Booking | null> => {
        try {
            const response = await api.getBooking({ bookingId });
            return response;
        } catch (err) {
            error.value = "Failed to fetch booking";
            console.error(err);
            return null;
        }
    };

    return {
        bookings,
        error,
        getBookingById,
        // ... other existing methods ...
    };
}); 