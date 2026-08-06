const API_URL = "http://127.0.0.1:8000";

export const predictGesture = async (base64Image = null) => {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image: base64Image }),
  });

  const data = await response.json();
  return data;
};