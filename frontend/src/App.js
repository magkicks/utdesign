import React, { useEffect, useState } from "react";
import TasksList from "./components/TasksList";
import axios from "axios";

const App = () => {
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/api/tasks/", {
                    headers: {
                        Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTMxMTgyLCJpYXQiOjE3MzQxMzAzNjAsImp0aSI6ImNkYzg5MGQ5NDgwYTQyYWM4NzlmMWU2NWUyZTlkNjc2IiwidXNlcl9pZCI6Nzl9.AJ20aag8rgTd-7aVcsFQFF8Lx5JHBUG38OGW_vQiuqM" // Replace with your actual token
                    }
                });
                setTasks(response.data);
            } catch (error) {
                console.error("Error fetching tasks:", error);
            }
        };

        fetchTasks();
    }, []);

    return (
        <div>
            <h1>Task Management</h1>
            <TasksList tasks={tasks} />
        </div>
    );
};

export default App;
