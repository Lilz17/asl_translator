const API_URL =
  "http://127.0.0.1:8000";

export const predictGesture =
  async () => {
    console.log(
      "Calling Backend..."
    );

    const response =
      await fetch(
        `${API_URL}/predict`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
        }
      );

    const data =
      await response.json();

    console.log(
      "Backend Response:",
      data
    );

    return data;
  };