'use strict';

// milisecond
const intervalMS = {
    '1m': 60000,
    '3m': 60000 * 3,
    '5m': 60000 * 5,
    '15m': 60000 * 15,
    '30m': 60000 * 30,
    '1h': 60000 * 60, // 15m x 4
    '4h': 60000 * 60 * 4,
    '8h': 60000 * 60 * 8,
    '12': 60000 * 60 * 12,
    '1d': 60000 * 60 * 24
};
const LIMIT = 500;

/**
 * Get time slot array
 * @param {Date} current - Current date object
 * @param {number} frame - frame count
 * @param {string} interval - frame interval
 * @returns {Array} - Time slot array
 */
const calcTimeSlot = (current, frame, interval) => {
    const slots = [];
    const range = intervalMS[interval] * LIMIT;
    let end = current.getTime();

    for (let i = 0; i < frame; i++) {
        let start = end - range;
        slots.push({
            startTime: start,
            endTime: end
        });
        end = start;
    }

    return slots;
};

/**
 * Get time slot array by start/end date
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @param {string} interval - frame interval
 * @returns {Array} - Time slot array
 */
const calcTimeSlotByDate = (startDate, endDate, interval) => {
    const slots = [];
    const range = intervalMS[interval] * LIMIT;
    let stop = false;
    let end = endDate.getTime();
    let start = startDate.getTime();

    while (!stop) {
        let tempStart = end - range;
        if (tempStart <= start) {
            tempStart = start;
            stop = true;
        }
        slots.push({
            startTime: tempStart,
            endTime: end
        });
        end = tempStart;
    }

    return slots;
};

const sleep = async (milliseconds) => {
    await new Promise(resolve => setTimeout(resolve, milliseconds));
}

/**
 * Create date time string for model
 * @param {number} longTime - Time in long type
 * @returns {string} - date time string format 2024-12-07 12:55:43 ( YYYY-MM-DD HH:MM:SS )
 */
const parseTimeString = (longTime) => {
    let date = new Date(longTime);
    let dateJSON = date.toJSON();
    return dateJSON.split('T').join(' ').split('.')[0];
};

/**
 * Create date string for model
 * @param {number} longTime - Time in long type
 * @returns {string} - date string format 2024-12-07 ( YYYY-MM-DD ) 
 */
const parseDateString = (longTime) => {
    let date = new Date(longTime);
    let dateJSON = date.toJSON();
    return dateJSON.split('T')[0];
};

module.exports = {
    calcTimeSlot,
    calcTimeSlotByDate,
    sleep,
    parseTimeString,
    parseDateString
};
