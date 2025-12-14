/**
 * Pomodoro Timer - JavaScript Logic
 *
 * Handles the countdown timer, start/pause/reset functionality,
 * and communication with the backend to save completed pomodoros.
 */

// Timer state
let timerInterval = null;
let timeRemaining = 25 * 60; // seconds
let isRunning = false;
let currentPomodoroId = null;
let selectedDuration = 25;

// Audio context for notification sound
let audioContext = null;

/**
 * Get CSRF token from meta tag.
 *
 * @returns {string} CSRF token value
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

/**
 * Play a notification sound using Web Audio API.
 * Creates a pleasant chime sound when the pomodoro completes.
 */
function playNotificationSound() {
    try {
        // Create audio context if it doesn't exist
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        // Resume context if suspended (browser autoplay policy)
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }

        const now = audioContext.currentTime;

        // Play a pleasant three-tone chime
        const frequencies = [523.25, 659.25, 783.99]; // C5, E5, G5 (C major chord)

        frequencies.forEach((freq, index) => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = freq;
            oscillator.type = 'sine';

            // Stagger the notes slightly
            const startTime = now + (index * 0.15);
            const duration = 0.5;

            gainNode.gain.setValueAtTime(0, startTime);
            gainNode.gain.linearRampToValueAtTime(0.3, startTime + 0.05);
            gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);

            oscillator.start(startTime);
            oscillator.stop(startTime + duration);
        });

    } catch (e) {
        console.log('Could not play notification sound:', e);
    }
}

// DOM Elements
const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');
const taskSelect = document.getElementById('taskSelect');
const durationRadios = document.querySelectorAll('input[name="duration"]');

/**
 * Format seconds as MM:SS string.
 *
 * @param {number} seconds - Total seconds
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Update the timer display.
 */
function updateDisplay() {
    timerDisplay.textContent = formatTime(timeRemaining);

    // Update page title with timer
    if (isRunning) {
        document.title = `${formatTime(timeRemaining)} - Pomodoro`;
    } else {
        document.title = 'Dashboard - Pomodoro Task Manager';
    }
}

/**
 * Start the pomodoro timer.
 */
async function startTimer() {
    if (isRunning) return;

    // Start a new pomodoro session in the backend
    const formData = new FormData();
    formData.append('duration', selectedDuration);
    if (taskSelect.value) {
        formData.append('task_id', taskSelect.value);
    }

    try {
        const response = await fetch('/pomodoro/start', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        const data = await response.json();
        currentPomodoroId = data.pomodoro_id;
    } catch (error) {
        console.error('Error starting pomodoro:', error);
    }

    isRunning = true;
    startBtn.disabled = true;
    pauseBtn.disabled = false;

    // Disable duration selection while running
    durationRadios.forEach(radio => radio.disabled = true);
    taskSelect.disabled = true;

    timerInterval = setInterval(() => {
        timeRemaining--;
        updateDisplay();

        if (timeRemaining <= 0) {
            completeTimer();
        }
    }, 1000);
}

/**
 * Pause the timer.
 */
function pauseTimer() {
    if (!isRunning) return;

    isRunning = false;
    clearInterval(timerInterval);

    startBtn.disabled = false;
    pauseBtn.disabled = true;
    startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Resume';
}

/**
 * Reset the timer to initial state.
 */
function resetTimer() {
    isRunning = false;
    clearInterval(timerInterval);

    timeRemaining = selectedDuration * 60;
    currentPomodoroId = null;

    startBtn.disabled = false;
    pauseBtn.disabled = true;
    startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start';

    // Re-enable controls
    durationRadios.forEach(radio => radio.disabled = false);
    taskSelect.disabled = false;

    updateDisplay();
    document.title = 'Dashboard - Pomodoro Task Manager';
}

/**
 * Complete the timer and save to backend.
 */
async function completeTimer() {
    clearInterval(timerInterval);
    isRunning = false;

    // Play notification sound
    playNotificationSound();

    // Show browser notification if permitted
    if (Notification.permission === 'granted') {
        new Notification('Pomodoro Complete!', {
            body: 'Great job! Take a break.',
            icon: '/static/img/tomato.png'
        });
    }

    // Mark pomodoro as complete in backend
    if (currentPomodoroId) {
        try {
            await fetch(`/pomodoro/${currentPomodoroId}/complete`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });
        } catch (error) {
            console.error('Error completing pomodoro:', error);
        }
    }

    // Show completion message
    alert('Pomodoro complete! Time for a break.');

    // Reset for next pomodoro
    resetTimer();

    // Reload page to update stats
    location.reload();
}

/**
 * Handle duration selection change.
 */
function handleDurationChange(event) {
    selectedDuration = parseInt(event.target.value);
    timeRemaining = selectedDuration * 60;
    updateDisplay();
}

// Event Listeners
if (startBtn) {
    startBtn.addEventListener('click', startTimer);
}

if (pauseBtn) {
    pauseBtn.addEventListener('click', pauseTimer);
}

if (resetBtn) {
    resetBtn.addEventListener('click', resetTimer);
}

durationRadios.forEach(radio => {
    radio.addEventListener('change', handleDurationChange);
});

// Request notification permission on load
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Initialize display
updateDisplay();
