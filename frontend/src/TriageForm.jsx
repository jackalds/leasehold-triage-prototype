import { useEffect, useId, useRef, useState } from "react";

const API_BASE = "http://localhost:8000/api";

function TriageForm({ onResult }) {
	const [scenarios, setScenarios] = useState([]);
	const [text, setText] = useState("");
	const [validationError, setValidationError] = useState("");
	const [submitError, setSubmitError] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);
	const textareaRef = useRef(null);
	const textId = useId();
	const errorId = useId();
	const scenariosHeadingId = useId();

	useEffect(() => {
		fetch(`${API_BASE}/categories/`)
			.then((response) => response.json())
			.then((categories) =>
				setScenarios(
					[...categories].sort((a, b) =>
						a.slug === "not-sure" ? 1 : b.slug === "not-sure" ? -1 : 0
					)
				)
			)
			.catch(() => setScenarios([]));
	}, []);

	async function submitTriage(body) {
		setIsSubmitting(true);
		setSubmitError("");
		try {
			const response = await fetch(`${API_BASE}/triage/`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(body),
			});
			if (!response.ok) {
				throw new Error("Request failed");
			}
			const data = await response.json();
			onResult(data);
		} catch {
			setSubmitError(
				"Sorry, something went wrong checking your situation. Please try again."
			);
		} finally {
			setIsSubmitting(false);
		}
	}

	function handleTextSubmit(event) {
		event.preventDefault();
		if (!text.trim()) {
			setValidationError(
				"Please describe your situation, or choose an option below."
			);
			textareaRef.current?.focus();
			return;
		}
		setValidationError("");
		submitTriage({ text: text.trim() });
	}

	function handleScenarioClick(slug) {
		setValidationError("");
		submitTriage({ scenario_id: slug });
	}

	return (
		<section aria-labelledby="triage-heading">
			<h2 id="triage-heading">Tell us what's going on</h2>

			<form onSubmit={handleTextSubmit} noValidate>
				<label htmlFor={textId}>Describe your situation in your own words</label>
				<textarea
					id={textId}
					name="text"
					rows={4}
					ref={textareaRef}
					value={text}
					onChange={(event) => setText(event.target.value)}
					aria-invalid={validationError ? "true" : undefined}
					aria-describedby={validationError ? errorId : undefined}
				/>
				{validationError && (
					<p id={errorId} role="alert" className="field-error">
						{validationError}
					</p>
				)}
				<button type="submit" disabled={isSubmitting}>
					Check my situation
				</button>
			</form>

			{scenarios.length > 0 && (
				<div className="scenarios">
					<h3 id={scenariosHeadingId}>Or choose a common situation</h3>
					<ul aria-labelledby={scenariosHeadingId}>
						{scenarios.map((category) => (
							<li key={category.slug}>
								<button
									type="button"
									onClick={() => handleScenarioClick(category.slug)}
									disabled={isSubmitting}
								>
									{category.name}
								</button>
							</li>
						))}
					</ul>
				</div>
			)}

			<p role="status" aria-live="polite" className="visually-hidden">
				{isSubmitting ? "Checking your situation…" : ""}
			</p>

			{submitError && (
				<p role="alert" className="field-error">
					{submitError}
				</p>
			)}
		</section>
	);
}

export default TriageForm;
