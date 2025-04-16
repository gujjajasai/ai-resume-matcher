import axios from 'axios';

const login = async (username, password) => {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post("http://127.0.0.1:8000/token/", formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const token = response.data.access_token;

        if (token) {
            localStorage.setItem("token", token); // Store token in localStorage
            return token;
        } else {
            throw new Error("Invalid response: No token received.");
        }
    } catch (error) {
        console.error("Login failed:", error.response?.data?.detail || error.message);
        throw new Error(error.response?.data?.detail || "Login failed. Please try again.");
    }
};

export default login;
