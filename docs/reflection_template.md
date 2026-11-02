# Assignment 5: Reflection

## Part 1: LangGraph Workflow

1. How did you design the 8-node workflow? What considerations influenced the order of approval stages?
 I designed the 8-node workflow to process financial requests step by step. First, the request is checked for errors, then the risk level is determined. Based on the risk and budget, the request goes through the required approvals. Low-risk requests need fewer approvals, while high-risk requests need more. This makes sure each request is reviewed properly before it is approved or rejected.

2. Describe your experience implementing the `interrupt()` pattern. What was intuitive and what was challenging?
Implementing interrupt() helped me understand how to pause the workflow and wait for human approval for high risk requests. It was easy to understand why we need it for manager and finance reviews.

3. How do the routing functions control the workflow? Why are conditional edges important for approval systems?
Routing functions decide which step the workflow should follow based on the request's risk level, budget, and approval decisions. Conditional edges are important because different requests need different approval steps. They help make sure each request follows the correct path before being approved or rejected.

## Part 2: Safety Guardrails

1. What types of attacks does your input validation protect against? Are there any gaps?
My input validation protects against invalid amounts, unauthorized departments, and some prompt injection attempts by checking for suspicious text. It also limits input length. However attackers may still find ways to bypass these checks. Authentication and authorization should also be added to make sure only authorized users can access the system and approve requests.
2. How did you implement PII masking? What trade-offs exist between security and usability?
I implemented PII masking using regular expressions to hide sensitive information like Social Security numbers, credit card numbers, emails, and phone numbers. This helps protect personal information. The trade-off is that hiding too much information can make it harder for users to understand or verify details. 

3. Why is output filtering important in financial systems, even when inputs are validated?
Output filtering is important because even if inputs are validated, the AI may still generate sensitive information or unsafe responses. In financial systems, output filtering helps prevent personal and financial information from being exposed. It provides an extra layer of security and helps protect user data.

## Part 3: CopilotKit Frontend

1. How does the `useLangGraphInterrupt` hook connect the frontend to the backend workflow?
The useLangGraphInterrupt hook connects the frontend to the backend by detecting when the workflow pauses for human approval. It displays the approval request to the user, collects their decision, and sends it back to the backend. The workflow then resumes based on whether the request was approved or rejected.

2. Describe the user experience when an approval interrupt fires. How did you design the UI to be clear and actionable?
When an approval interrupt happens, the workflow pauses and shows the request details to the reviewer. I designed the UI to clearly display the amount, risk level, and reason for the request, along with Approve and Reject options. The reviewer can also add comments. Once they submit their decision, the workflow continues.
3. What challenges did you face integrating CopilotKit with the LangGraph backend?
I didn't face any challenges integrating CopilotKit with LangGraph. The integration was already implemented.

## Part 4: LangSmith Evaluation

1. How does your risk accuracy evaluator handle partial matches (adjacent risk levels)?
My risk accuracy evaluator gives a score of 1.0 for an exact match, 0.5 when the risk levels are next to each other (like medium and high), and 0.0 when they are more than one level apart.

2. Why is evaluation important for production AI systems? How would you extend the evaluation suite?
Evaluation is important because it helps make sure AI systems are accurate, reliable, and safe before and after deployment. I would extend my evaluation suite by adding more edge cases, testing different approval scenarios, and monitoring real-world results to identify errors and improve the system.

3. What insights did the evaluation results reveal about your workflow's behavior?
The evaluation results helped me understand how risk levels, approval paths, and human reviews are checked. They showed that the evaluators were working correctly, but more testing with the actual agent is needed to confirm the workflow behaves as expected. 
## Bonus Features (if implemented)

1. Describe any bonus features you implemented and the design decisions behind them.

## Key Learnings

- Learned how to build AI workflows using LangGraph.
- Implemented human-in-the-loop approvals using interrupt().
- Added input validation and PII masking to improve security.
- Learned how to use CopilotKit to connect the frontend and backend.
- Used LangSmith and RAGAS to understand AI evaluation and testing.

## Ideas for Improvement

- Add authentication and authorization to improve security.
- Test the actual AI agent to measure its accuracy.
- Allow manager and finance approvals to happen in parallel.
