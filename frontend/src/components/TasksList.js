import React, { useEffect, useState } from "react";
import axios from "axios";

const TasksList = () => {
  const [tasks, setTasks] = useState([]); // State to store tasks
  const [error, setError] = useState(null); // State to store any errors

  useEffect(() => {
    // Fetch tasks when the component loads
    const fetchTasks = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/tasks/", {
          headers: {
            Authorization: "Bearer <your-access-token>", // Replace with your access token
          },
        });
        setTasks(response.data); // Update state with the fetched tasks
      } catch (err) {
        setError(err.response ? err.response.data : "Error fetching tasks");
      }
    };

    fetchTasks();
  }, []); // Empty dependency array ensures this runs once when the component mounts

  return (
    <div>
      <h2>Tasks List</h2>
      {error ? (
        <p style={{ color: "red" }}>Error: {error}</p>
      ) : (
        <ul>
          {tasks.map((task) => (
            <li key={task.id}>
              <strong>{task.title}</strong>: {task.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TasksList;
