import { useState } from "react";
import TriageForm from "./TriageForm.jsx";
import ResultsScreen from "./ResultsScreen.jsx";

function App() {
	const [result, setResult] = useState(null);

	return (
		<>
			<header className="app-header">
				<h1>Leasehold triage prototype</h1>
				<span className="badge">Prototype — not a real advice service</span>
			</header>
			<main>
				<TriageForm onResult={setResult} />
				{result && <ResultsScreen result={result} />}
			</main>
		</>
	);
}

export default App;
