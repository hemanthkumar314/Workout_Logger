let chart = null;

document.addEventListener('DOMContentLoaded', function() {
    const selectElement = document.getElementById('workout-select');
    selectElement.addEventListener('change', fetchWorkoutData);
});

function fetchWorkoutData() {
    const selectedWorkout = document.getElementById('workout-select').value;
    if (!selectedWorkout) return;

    fetch(`/api/workout/${selectedWorkout}`)
        .then(response => response.json())
        .then(data => updateChart(data, selectedWorkout));
}

function updateChart(workoutData, workoutName) {
    const ctx = document.getElementById('workoutChart').getContext('2d');

    if (chart) {
        chart.destroy();
    }

    console.log('Workout Data:', workoutData);

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: workoutData.map(w => w.date),
            datasets: [{
                label: workoutName,
                data: workoutData.map(w => w.count),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
    });
}