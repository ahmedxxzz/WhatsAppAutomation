## **A. System Overview**

**Project Name:** Local WhatsApp Automation Suite (L-WAS) v2.1

**Description:**
L-WAS v2.1 is a desktop automation solution for sending personalized WhatsApp messages. This version retains the **Multi-Session Scheduler** but introduces a precise **Fixed Delay Rate Control** system, replacing the previous "messages per minute" logic.

**Architecture:**
*   **Frontend:** Python/CustomTkinter.
*   **Backend:** Node.js `wppconnect` bridge.
*   **Timing:**
    *   **Scheduler:** Determines *if* the worker is allowed to run based on Time of Day.
    *   **Rate Controller:** Determines the *exact pause duration* between messages (e.g., "Sleep 5 seconds").

---

## **B. Functional Requirements (Updated)**

### **1. Scheduling (Multi-Session)**
*   (Unchanged) Users define multiple active windows per day (e.g., Mon 09:00-12:00 AND 14:00-16:00).

### **2. Rate Limiting (NEW: Fixed Delay)**
*   **Input:** "Message Delay" (in seconds).
*   **Data Type:** Positive number (Integer or Float). Examples: `5`, `1.5`, `10`.
*   **Logic:**
    1.  Worker sends a message.
    2.  Worker receives response (Success/Fail).
    3.  Worker **immediately sleeps** for `X` seconds defined in the input.
    4.  Worker proceeds to the next contact.
*   **Constraint:** Input must be $> 0$.
*   **Interaction with Retries:** If a network error occurs, internal retries happen *within* the send attempt. The fixed delay occurs *after* the final outcome of that attempt is resolved.

### **3. CSV Processing & Logging**
*   (Unchanged) Load CSV -> Filter against `worked.csv` -> Log results.

### **4. GUI Dashboard (Updated)**
*   **Global Settings Area:**
    *   **Removed:** "Messages per Minute" input.
    *   **Added:** "Message Delay (seconds)" input.
*   **Validation:** Prevent non-numeric input or negative numbers.

---

## **D. Data Flow Diagram (Updated)**

```mermaid
graph TD
    A[Worker Thread] --> B{Is Schedule Active?}
    B -- No --> C[Sleep 30s]
    B -- Yes --> D[Process Contact]
    D --> E[Send HTTP Request]
    E --> F{Result?}
    F --> G[Log Success/Fail]
    G --> H[**SLEEP Fixed Delay (e.g., 5s)**]
    H --> A
```

---

## **E. Flowchart (Worker Execution)**

```text
[START WORKER]
   |
   v
[Load Queue]
   |
   v
[LOOP: While Queue Not Empty]
   |
   +-> [Check Pause/Stop?]
   |
   +-> [Check Schedule (Multi-Session)?] --(No)--> [Wait]
   |
   +-> (Yes)
   |
   v
[Pop Contact] -> [Generate Msg] -> [POST to Node.js]
   |
   v
[Receive Response]
   |
   +-> (Success) -> [Log worked.csv]
   +-> (Fail)    -> [Log failed.csv]
   |
   v
[**SLEEP: Configured Delay (X seconds)**]  <-- UPDATED STEP
   |
   v
[Loop]
```

---

## **F. Sequence Diagram (Timing)**

1.  **Worker** calls `NodeClient.send_message()`.
2.  **NodeClient** returns `200 OK`.
3.  **Worker** updates GUI Progress.
4.  **Worker** reads `delay_seconds` from config.
5.  **Worker** executes `time.sleep(delay_seconds)`.
6.  **Worker** begins next iteration.

---

## **H. README Update (Configuration)**

### **Global Settings**
*   **Message Delay (s):** The exact time in seconds to wait *after* sending a message before starting the next one.
    *   *Recommended:* `5` to `15` seconds to avoid spam detection.
    *   *Minimum:* `1` second.
*   **Done Number:** Phone number to receive a notification when the batch finishes.