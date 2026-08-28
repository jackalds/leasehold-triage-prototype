import { useState } from "react";
import TriageForm from "./TriageForm.jsx";

function App() {
	const [result, setResult] = useState(null);

	return (
		<main>
			<h1>Leasehold triage prototype</h1>
			<TriageForm onResult={setResult} />
			{/* Placeholder pending the T5 results screen: shows the raw top match. */}
			{result && (
				<section aria-labelledby="result-heading">
					<h2 id="result-heading">
						{result.confident ? "This looks like:" : "We're not sure"}
					</h2>
					<p>{result.matches[0].category.name}</p>
					<p>{result.matches[0].category.summary}</p>
					<p>{result.matches[0].category.next_step}</p>
				</section>
			)}
		</main>
	);
}

export default App;
