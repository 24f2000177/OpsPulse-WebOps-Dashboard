async function updateDashboard() {

    try {

        const response = await fetch("/api/system");

        const data = await response.json();

        document.getElementById("cpu").innerText =
            data.cpu + "%";

        document.getElementById("memory").innerText =
            data.memory + "%";

        document.getElementById("disk").innerText =
            data.disk + "%";

        document.getElementById("hostname").innerText =
            data.hostname;

        document.getElementById("os").innerText =
            data.os;

        document.getElementById("uptime").innerText =
            data.uptime;

        document.getElementById("status").innerText =
            data.status;

        document.getElementById("last_updated").innerText =
            data.last_updated;

    }

    catch (error) {

        console.log(error);

    }

}

updateDashboard();

setInterval(updateDashboard, 2000);