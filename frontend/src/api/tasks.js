import apiClient from "./axios";

export const getTasks = async () => {
    try {
        const response = await apiClient.get("tasks/");
        return response.data;
    } catch (error) {
        console.error("Error fetching tasks:", error);
        return [];
    }
};
