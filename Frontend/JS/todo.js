async function loadLists() {
    try {
        const response = await fetch('http://127.0.0.1:8000/lists');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const lists = await response.json();
        console.log(lists);
        displayLists(lists);
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function loadTasks(listId, listName) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/lists/${listId}/tasks`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const tasks = await response.json();
        displayTasks(tasks, listName, listId);
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function createList(name) {
    try {
        const response = await fetch('http://127.0.0.1:8000/lists', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'name': name})
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const list = await response.json();
        console.log(list);
        loadLists();
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function createTask(listId, name, listName) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/lists/${listId}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'name': name})
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const task = await response.json();
        loadTasks(listId, listName);
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function deleteList(listId) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/lists/${listId}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        loadLists();
    } catch (error) {
        console.error('There was an error!', error);
    }
}

async function deleteTask(listId, taskId) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/lists/${listId}/tasks/${taskId}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        loadTasks(listId);
    } catch (error) {
        console.error('There was an error!', error);
    }
}
function displayLists(lists) {
    const existingContainer = document.getElementById('list-container');
    if (existingContainer) {
        existingContainer.remove();
    }

    const existingHeading = document.getElementById('task-heading');
    if (existingHeading) {
        existingHeading.remove();
    }

    const existingMenuHeading = document.getElementById('tasklist-heading');
    if (existingMenuHeading) {
        existingMenuHeading.remove();
    }

    const heading = document.createElement('h1');
    heading.className = 'title';
    heading.textContent = 'Deine Todo-Listen';
    heading.id = 'tasklist-heading';
    const division = document.createElement('div');
    division.className = 'lists_div';
    division.id = 'list-container';
    const listContainer = document.createElement('ul');
    listContainer.id = 'list-container';
    listContainer.className = 'list_container';

    lists.forEach(list => {
        if (list.name) {
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = '#'; // dummy href
        link.textContent = list.name;
        link.onclick = function() {
            loadTasks(list.id, list.name);
            return false;
        };
        const deleteButton = createDeleteButton();
        deleteButton.onclick = function() {
            deleteList(list.id);
            return false;
        };
        listItem.appendChild(link);
        listItem.appendChild(deleteButton);
        listContainer.appendChild(listItem);
        }
        else {
            console.warn('List name is empty', list);
        }
    });
    const form = document.createElement('form');
    const input = document.createElement('input');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const name = document.getElementById('list_name').value;
        createList(name);
        return false;
    })
    input.type = 'text';
    input.placeholder = 'List Name';
    input.name = 'list_name';
    input.id = 'list_name';

    form.appendChild(input);
    listContainer.appendChild(form);
    division.appendChild(listContainer);
    document.body.appendChild(heading);
    document.body.appendChild(division);
}

function displayTasks(tasks, listName, listId) {
    const listContainer = document.getElementById('list-container');
    if (listContainer) {
        listContainer.remove();
    }
    const existingContainer = document.getElementById('task-container');
    if (existingContainer) {
        existingContainer.remove();
    }

    const existingHeading = document.getElementById('tasklist-heading');
    if (existingHeading) {
        existingHeading.remove();
    }

    const existingMenuHeading = document.getElementById('task-heading');
    if (existingMenuHeading) {
        existingMenuHeading.remove();
    }

    const heading = document.createElement('h1');
    heading.className = 'title';
    heading.textContent = listName;
    heading.id = 'task-heading';

    const division = document.createElement('div');
    division.className = 'tasks_div';
    division.id = 'task-container';
    const taskContainer = document.createElement('ul');
    taskContainer.className = 'task_container';

    tasks.forEach(task => {
        if (task.name) {
            const listItem = document.createElement('li');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `task-${task.id}`;
            checkbox.name = task.name;
            checkbox.onclick = function() {
                checkTask(task.list_id, task.id);
            }

            const label = document.createElement('label');
            label.htmlFor = `task-${task.id}`;
            label.textContent = task.name;

            const deleteButton = createDeleteButton()
            deleteButton.onclick = function() {
                deleteTask(task.list_id, task.id);
                return false;
            };
            listItem.appendChild(checkbox);
            listItem.appendChild(label);
            listItem.appendChild(deleteButton);
            taskContainer.appendChild(listItem);
        } else {
            console.warn('Task name is empty', task);
        }
    });

    const form = document.createElement('form');
    const input = document.createElement('input');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const name = document.getElementById('task_name').value;
        createTask(listId, name, listName);
        return false;
    })
    input.type = 'text';
    input.placeholder = 'Task Name';
    input.name = 'task_name';
    input.id = 'task_name';
    form.appendChild(input);
    taskContainer.appendChild(form);
    division.appendChild(taskContainer);
    document.body.appendChild(heading);
    document.body.appendChild(division);
}

function createDeleteButton() {
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.textContent = 'X';
    
    return deleteButton;
}