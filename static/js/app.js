function showContent(type) {
    document.getElementById("admin-login").style.display = (type === "admin") ? "block" : "none";
    document.getElementById("user-login").style.display = (type === "user") ? "block" : "none";

    if (type === "admin") {
        document.getElementById("admin_button").classList.add('active')
        document.getElementById("user_button").classList.remove('active')
    }
    else if (type === "user") {
        document.getElementById("admin_button").classList.remove('active')
        document.getElementById("user_button").classList.add('active')
    }

}

window.onload = function () {
    document.getElementById("admin_button").classList.add('active')
    showContent("admin")
};

async function startQuiz(num) {
    try {
        const response = await fetch(`/start_quiz`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ min: num })
        });
        const data = await response.json();
        console.log("Start Quiz Response:", data);
        
        if (data.message === "Quiz started") {
            fetchRemainingTime();  
        }
    } catch (error) {
        console.error("Error starting quiz:", error);
    }
}

async function fetchRemainingTime() {
    const timer = document.getElementById("timer")
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/time_remaining`);
            const data = await response.json();
            
            if (response.ok) {
                let temp = `${Math.floor(data.remaining_time / 60)}:${Math.floor(data.remaining_time % 60).toString().padStart(2, '0')}`
                timer.textContent = temp
                
                if (data.remaining_time <= 0) {
                    console.log("Time's up!");
                    document.getElementById("submit").click();
                    clearInterval(interval);  
                }
            } else {
                console.error("Error:", data);
                clearInterval(interval);  
            }
        } catch (error) {
            console.error("Error fetching time:", error);
            clearInterval(interval);  
        }
    }, 1000);
}

async function fetchData(route) {
    const response = await fetch(route);
    const data = await response.json();
    return data;
}

async function renderChartUser() {
    const data = await fetchData('/chart-data');

    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: {
                  position: 'top',
                },
                title: {
                  display: true,
                  text: 'Performance of Past 5 Tests'
                }
            }
        }
    });
}

async function renderHistogram(quiz_id) {
    const data = await fetchData('/histogram?quiz_id='+quiz_id);

    const ctx = document.getElementById('histo'+quiz_id).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: {
                  position: 'top',
                },
                title: {
                  display: true,
                  text: 'Quiz Performance'
                }
            }
        }
    });
}

async function fetchQuizData(quiz_id) {

    try {
        const response = await fetch('/quizdata?quiz_id='+quiz_id);

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('totalAttempts'+quiz_id).innerText = data.total_attempts;
        document.getElementById('averageScore'+quiz_id).innerText = data.average.toFixed(2) + "%"; 
        document.getElementById('standardDeviation'+quiz_id).innerText = data.stdev.toFixed(2);
    } catch (error) {
        console.error("Error fetching quiz data:", error);
        alert("Failed to fetch quiz data.");
    }

}

async function fetchUserStatistics() {

    try {
        const response = await fetch('/userStatistics');

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('totalAttemptsUser').innerText = data.totalAttempts;
        document.getElementById('averagePercentageUser').innerText = data.average.toFixed(2) + "%"; 
        document.getElementById('standardDeviationUser').innerText = data.stdev.toFixed(2);
    } catch (error) {
        console.error("Error fetching quiz data:", error);
        alert("Failed to fetch quiz data.");
    }

}