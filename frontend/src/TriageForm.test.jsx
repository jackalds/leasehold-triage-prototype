import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TriageForm from "./TriageForm.jsx";

const CATEGORIES = [
	{ slug: "not-sure", name: "Not sure / something else" },
	{ slug: "service-charges", name: "Service charges" },
];

const TRIAGE_RESULT = {
	confident: true,
	matches: [
		{
			category: {
				slug: "service-charges",
				name: "Service charges",
				summary: "This usually means...",
				next_step: "Read the guide.",
				guide_link: "https://www.lease-advice.org/service-charges",
				is_urgent: false,
			},
			confidence: 0.95,
		},
	],
};

function mockFetchSequence(...responses) {
	const fetchMock = vi.fn();
	for (const response of responses) {
		fetchMock.mockImplementationOnce(() =>
			Promise.resolve({ ok: true, json: () => Promise.resolve(response) })
		);
	}
	globalThis.fetch = fetchMock;
	return fetchMock;
}

describe("TriageForm", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
	});

	it("submits free text and reports the result", async () => {
		mockFetchSequence(CATEGORIES, TRIAGE_RESULT);
		const onResult = vi.fn();
		const user = userEvent.setup();

		render(<TriageForm onResult={onResult} />);

		await screen.findByText("Service charges");

		await user.type(
			screen.getByLabelText("Describe your situation in your own words"),
			"I got an invoice for a service charge"
		);
		await user.click(screen.getByRole("button", { name: "Check my situation" }));

		await waitFor(() => expect(onResult).toHaveBeenCalledWith(TRIAGE_RESULT));
	});

	it("shows a validation error and refocuses the textarea on empty submit", async () => {
		mockFetchSequence(CATEGORIES);
		const onResult = vi.fn();
		const user = userEvent.setup();

		render(<TriageForm onResult={onResult} />);
		await screen.findByText("Service charges");

		await user.click(screen.getByRole("button", { name: "Check my situation" }));

		expect(
			await screen.findByText(
				"Please describe your situation, or choose an option below."
			)
		).toBeInTheDocument();
		expect(
			screen.getByLabelText("Describe your situation in your own words")
		).toHaveFocus();
		expect(onResult).not.toHaveBeenCalled();
	});

	it("submits a scenario id when a scenario button is clicked", async () => {
		mockFetchSequence(CATEGORIES, TRIAGE_RESULT);
		const onResult = vi.fn();
		const user = userEvent.setup();

		render(<TriageForm onResult={onResult} />);
		const button = await screen.findByRole("button", { name: "Service charges" });

		await user.click(button);

		await waitFor(() => expect(onResult).toHaveBeenCalledWith(TRIAGE_RESULT));
		expect(globalThis.fetch).toHaveBeenLastCalledWith(
			expect.stringContaining("/triage/"),
			expect.objectContaining({
				body: JSON.stringify({ scenario_id: "service-charges" }),
			})
		);
	});
});
