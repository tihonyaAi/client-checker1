<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AurumTrade - Проверка ников</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0b0e11;
            color: #f0b90b;
            margin: 0;
            padding: 20px;
        }
        #message {
            margin-bottom: 10px;
            font-size: 1rem;
            min-height: 24px;
        }
        #nickname-input {
            width: 300px;
            padding: 10px;
            font-size: 1.2rem;
            border-radius: 8px;
            border: 1px solid #f0b90b;
            background-color: #1e2329;
            color: white;
            outline: none;
        }
        #check-btn {
            padding: 10px 20px;
            margin-left: 10px;
            font-size: 1.2rem;
            background-color: #f0b90b;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: #0b0e11;
        }
        #check-btn:hover {
            background-color: #d9a308;
        }
        #history-list {
            margin-top: 20px;
            max-width: 500px;
            list-style: none;
            padding: 0;
            max-height: 300px;
            overflow-y: auto;
            background-color: #1e2329;
            border-radius: 8px;
            padding: 15px;
        }
        #history-list li {
            padding: 5px 0;
            border-bottom: 1px solid #2a2f35;
        }
        #history-list li.green {
            color: #4CAF50; /* зеленый */
        }
        #history-list li.red {
            color: #f44336; /* красный */
        }
    </style>
</head>
<body>
    <h1>AurumTrade - Проверка ников</h1>

    <div id="message"></div>

    <input id="nickname-input" type="text" placeholder="Введите ник" autocomplete="off" />
    <button id="check-btn">Проверить</button>

    <ul id="history-list"></ul>

    <script>
        const input = document.getElementById("nickname-input");
        const btn = document.getElementById("check-btn");
        const message = document.getElementById("message");
        const historyList = document.getElementById("history-list");

        // Получаем токен из localStorage (получен при логине)
        const token = localStorage.getItem("token");

        async function checkNicknames() {
            const nick = input.value.trim();
            if (!nick) {
                message.textContent = "⚠ Введите ник";
                return;
            }
            message.textContent = "";

            try {
                const res = await fetch("/check", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ nicknames: [nick] })
                });

                if (!res.ok) throw new Error("Ошибка при проверке ника");

                const data = await res.json();
                // Показать статус над вводом
                const status = data.results[0].status;
                if (status === "Не найдено") {
                    message.style.color = "#4CAF50";
                    message.textContent = `✅ Ник "${nick}" свободен`;
                } else {
                    message.style.color = "#f44336";
                    message.textContent = `❌ Ник "${nick}" занят`;
                }

                input.value = "";
                await loadHistory();
            } catch (err) {
                message.style.color = "red";
                message.textContent = "Ошибка: " + err.message;
            }
        }

        async function loadHistory() {
            try {
                const res = await fetch("/history", {
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });
                if (!res.ok) throw new Error("Ошибка при загрузке истории");

                const data = await res.json();

                historyList.innerHTML = "";
                data.forEach(item => {
                    const li = document.createElement("li");
                    li.textContent = item;

                    if (item.includes("Не найдено")) {
                        li.classList.add("green");
                    } else if (item.includes("Ник занят")) {
                        li.classList.add("red");
                    }

                    historyList.appendChild(li);
                });
            } catch (err) {
                message.style.color = "red";
                message.textContent = "Ошибка: " + err.message;
            }
        }

        btn.addEventListener("click", () => {
            checkNicknames();
        });

        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                checkNicknames();
            }
        });

        window.onload = () => {
            if (!token) {
                message.style.color = "red";
                message.textContent = "❌ Токен не найден. Пожалуйста, войдите.";
                return;
            }
            loadHistory();
        };
    </script>
</body>
</html>
