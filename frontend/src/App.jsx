import { useEffect, useState } from "react";

function App() {
	const [status, setStatus] = useState("loading");

	useEffect(() => {
		fetch("http://localhost:8000/api/health/")
			.then((response) => response.json())
			.then((data) => setStatus(data.status))
			.catch(() => setStatus("error"));
	}, []);

	return (
		<main>
			<h1>Leasehold triage prototype</h1>
			<p>Backend status: {status}</p>
		</main>
	);
}

export default App;
