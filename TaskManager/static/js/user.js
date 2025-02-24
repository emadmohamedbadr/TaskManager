let tasks = [];

document.addEventListener("DOMContentLoaded", () => {
    loadTasks();
});

// Load Tasks from LocalStorage
function loadTasks() {
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
        tasks = JSON.parse(savedTasks);
        displayTasks('all');
    }
}

// Display Tasks
function displayTasks(filter) {
    const tasksGrid = document.querySelector(".tasks-grid");
    tasksGrid.innerHTML = '';
    
    let filteredTasks = tasks;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    switch (filter) {
        case 'all':
            filteredTasks = tasks;
            break;
        case 'upcoming':
            filteredTasks = tasks.filter(task => new Date(task.deadline) > new Date());
            break;
        case 'current':
            filteredTasks = tasks.filter(task => {
                const taskDate = new Date(task.deadline);
                taskDate.setHours(0, 0, 0, 0);
                return taskDate.getTime() === today.getTime();
            });
            break;
        case 'delayed':
            filteredTasks = tasks.filter(task => new Date(task.deadline) < new Date() && task.status !== 'completed');
            break;
        default:
            filteredTasks = tasks;
    }

    // Sort tasks by priority
    filteredTasks.sort((a, b) => {
        const priorityOrder = { high: 1, medium: 2, low: 3 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
    });

    if (filteredTasks.length === 0) {
        tasksGrid.innerHTML = '📋 <span class="lang-no-tasks">No tasks available</span>';
        return;
    }
    
    filteredTasks.forEach((task, index) => {
        let div = document.createElement('div');
        div.className = `task-item ${task.priority}`;

        const isDelayed = new Date(task.deadline) < new Date() && task.status !== 'completed';
        if (isDelayed) {
            div.classList.add('delayed');
        }

        div.innerHTML = `
            <h3>📌 ${task.name}</h3>
            <p>👤 Employee: ${task.employee}</p>
            <p>📝 ${task.description}</p>
            <p>🕒 ${new Date(task.deadline).toLocaleString()}</p>
            <p>Status: ${task.status}</p>
            ${isDelayed ? '<p class="warning">⚠️ This task is delayed!</p>' : ''}
        `;
        tasksGrid.appendChild(div);
    });
}

// Filter Tasks
function filterTasks(status) {
    displayTasks(status);
}

// Logout Function
function logout() {
    const confirmLogout = confirm("Are you sure you want to logout?");
    if (confirmLogout) {
        window.location.href = "../index.html";
    }
}
