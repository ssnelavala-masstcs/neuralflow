# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: app.spec.ts >> NeuralFlow E2E Tests >> 10 - Workflow list and creation
- Location: e2e/app.spec.ts:132:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Execution Mode').first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Execution Mode').first()

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]:
    - button "Canvas" [ref=e5] [cursor=pointer]:
      - img [ref=e6]
      - text: Canvas
    - button "Templates" [ref=e10] [cursor=pointer]:
      - img [ref=e11]
      - text: Templates
    - button "Cost" [ref=e16] [cursor=pointer]:
      - img [ref=e17]
      - text: Cost
  - generic [ref=e19]:
    - banner [ref=e20]:
      - img [ref=e21]
      - generic [ref=e24]: NeuralFlow
      - generic [ref=e25]:
        - generic "Reconnecting…" [ref=e26]:
          - img [ref=e27]
          - generic [ref=e29]: Reconnecting…
        - generic [ref=e30]: Connecting to sidecar…
        - button "Undo (Ctrl+Z)" [disabled] [ref=e31]:
          - img [ref=e32]
        - button "Redo (Ctrl+Shift+Z)" [disabled] [ref=e35]:
          - img [ref=e36]
        - button "Run" [disabled] [ref=e39]:
          - img [ref=e40]
          - text: Run
        - button "Export" [disabled] [ref=e42]:
          - img [ref=e43]
          - text: Export
        - button "Templates" [ref=e47] [cursor=pointer]:
          - img [ref=e48]
          - text: Templates
        - button "Properties" [ref=e53] [cursor=pointer]:
          - img [ref=e54]
          - text: Properties
        - button "Settings" [ref=e57] [cursor=pointer]:
          - img [ref=e58]
        - button "Remote Connection" [ref=e61] [cursor=pointer]:
          - img [ref=e62]
        - button "Notifications" [ref=e66] [cursor=pointer]:
          - img [ref=e67]
    - generic [ref=e72]:
      - generic [ref=e73]:
        - button "Select workspace" [ref=e76] [cursor=pointer]:
          - img [ref=e77]
          - generic [ref=e79]: Select workspace
          - img [ref=e80]
        - generic [ref=e82]:
          - generic [ref=e83]: Workflows
          - button "New workflow" [ref=e84] [cursor=pointer]:
            - img [ref=e85]
        - paragraph [ref=e88]: No workflows yet.
        - generic [ref=e90]:
          - paragraph [ref=e91]: Nodes
          - generic "AI model with tools" [ref=e92]:
            - img [ref=e94]
            - generic [ref=e97]:
              - paragraph [ref=e98]: Agent
              - paragraph [ref=e99]: AI model with tools
          - generic "Unit of work" [ref=e100]:
            - img [ref=e102]
            - generic [ref=e105]:
              - paragraph [ref=e106]: Task
              - paragraph [ref=e107]: Unit of work
          - generic "Built-in or MCP tool" [ref=e108]:
            - img [ref=e110]
            - generic [ref=e112]:
              - paragraph [ref=e113]: Tool
              - paragraph [ref=e114]: Built-in or MCP tool
          - generic "Start workflow" [ref=e115]:
            - img [ref=e117]
            - generic [ref=e119]:
              - paragraph [ref=e120]: Trigger
              - paragraph [ref=e121]: Start workflow
          - generic "Conditional branch" [ref=e122]:
            - img [ref=e124]
            - generic [ref=e128]:
              - paragraph [ref=e129]: Router
              - paragraph [ref=e130]: Conditional branch
          - generic "Vector / KV store" [ref=e131]:
            - img [ref=e133]
            - generic [ref=e137]:
              - paragraph [ref=e138]: Memory
              - paragraph [ref=e139]: Vector / KV store
          - generic "Approval checkpoint" [ref=e140]:
            - img [ref=e142]
            - generic [ref=e146]:
              - paragraph [ref=e147]: Human
              - paragraph [ref=e148]: Approval checkpoint
          - generic "Merge branches" [ref=e149]:
            - img [ref=e151]
            - generic [ref=e155]:
              - paragraph [ref=e156]: Aggregator
              - paragraph [ref=e157]: Merge branches
          - generic "Workflow result" [ref=e158]:
            - img [ref=e160]
            - generic [ref=e166]:
              - paragraph [ref=e167]: Output
              - paragraph [ref=e168]: Workflow result
          - generic "Nested workflow" [ref=e169]:
            - img [ref=e171]
            - generic [ref=e175]:
              - paragraph [ref=e176]: Subflow
              - paragraph [ref=e177]: Nested workflow
      - generic [ref=e178]:
        - application [ref=e181]:
          - img
          - generic "Control Panel" [ref=e184]:
            - button "Zoom In" [ref=e185] [cursor=pointer]:
              - img [ref=e186]
            - button "Zoom Out" [ref=e188] [cursor=pointer]:
              - img [ref=e189]
            - button "Fit View" [ref=e191] [cursor=pointer]:
              - img [ref=e192]
          - generic [ref=e195]:
            - button "Zoom In" [ref=e196] [cursor=pointer]:
              - img [ref=e197]
            - button "Zoom Out" [ref=e200] [cursor=pointer]:
              - img [ref=e201]
            - button "Fit View" [ref=e204] [cursor=pointer]:
              - img [ref=e205]
          - img "Mini Map" [ref=e211]
          - generic [ref=e213]:
            - img [ref=e215]
            - heading "Start Building Your Workflow" [level=3] [ref=e217]
            - paragraph [ref=e218]: Drag nodes from the left palette onto this canvas and connect them to create AI workflows.
            - generic [ref=e219]:
              - generic [ref=e220]:
                - generic [ref=e221]: "1"
                - text: Drag a
                - strong [ref=e222]: Trigger
                - text: node to start
              - generic [ref=e223]:
                - generic [ref=e224]: "2"
                - text: Add an
                - strong [ref=e225]: Agent
                - text: node and configure your model
              - generic [ref=e226]:
                - generic [ref=e227]: "3"
                - text: Connect nodes by dragging from one handle to another
              - generic [ref=e228]:
                - generic [ref=e229]: "4"
                - text: Add an
                - strong [ref=e230]: Output
                - text: node to capture results
            - paragraph [ref=e231]: 💡 Press Ctrl+K for the command palette or browse Templates for starter workflows.
          - link "React Flow attribution" [ref=e233] [cursor=pointer]:
            - /url: https://reactflow.dev
            - text: React Flow
        - generic [ref=e236]:
          - generic [ref=e237]:
            - button "Run Log" [ref=e238] [cursor=pointer]
            - button "History" [ref=e239] [cursor=pointer]
            - button "Debug" [ref=e240] [cursor=pointer]
            - button "Version History" [ref=e241] [cursor=pointer]
          - generic [ref=e243]:
            - generic [ref=e244]:
              - generic [ref=e245]: Run Log
              - generic [ref=e246]: idle
            - paragraph [ref=e248]: No run started yet. Press Run to execute the workflow.
```

# Test source

```ts
  35  |     await page.waitForTimeout(1500);
  36  |     const hasPalette = await page.locator("text=Type a command or search").isVisible().catch(() => false);
  37  |     if (hasPalette) {
  38  |       await expect(page.locator("text=Run Workflow")).toBeVisible();
  39  |       await expect(page.locator("text=Save Canvas")).toBeVisible();
  40  |       await expect(page.locator("text=Undo")).toBeVisible();
  41  |       await expect(page.locator("text=Redo")).toBeVisible();
  42  |       await expect(page.locator("text=Browse Templates")).toBeVisible();
  43  |       await page.keyboard.press("Escape");
  44  |       await page.waitForTimeout(500);
  45  |     }
  46  |     await page.keyboard.press("Control+k");
  47  |     await page.waitForTimeout(1500);
  48  |     await page.screenshot({ path: "e2e/screens/03-command-palette.png" });
  49  |     await page.keyboard.press("Escape");
  50  |   });
  51  | 
  52  |   test("04 - Drag and drop nodes onto canvas", async ({ page }) => {
  53  |     const triggerNode = page.locator("text=Trigger").first();
  54  |     const canvas = page.locator(".react-flow");
  55  |     await triggerNode.dragTo(canvas, { targetPosition: { x: 100, y: 200 } });
  56  |     await page.waitForTimeout(500);
  57  |     await expect(page.locator("text=Trigger").last()).toBeVisible();
  58  |     await page.screenshot({ path: "e2e/screens/04-dragged-trigger-node.png" });
  59  |   });
  60  | 
  61  |   test("05 - Add Agent node and configure it", async ({ page }) => {
  62  |     const canvas = page.locator(".react-flow");
  63  |     await page.locator("text=Trigger").first().dragTo(canvas, { targetPosition: { x: 100, y: 200 } });
  64  |     await page.waitForTimeout(300);
  65  |     await page.locator("text=Agent").first().dragTo(canvas, { targetPosition: { x: 350, y: 200 } });
  66  |     await page.waitForTimeout(300);
  67  |     await page.locator("text=Agent").last().click();
  68  |     await page.waitForTimeout(500);
  69  |     await expect(page.locator("text=Agent Properties")).toBeVisible();
  70  |     await page.screenshot({ path: "e2e/screens/05-agent-node-properties.png" });
  71  |   });
  72  | 
  73  |   test("06 - Undo/Redo works", async ({ page }) => {
  74  |     const canvas = page.locator(".react-flow");
  75  |     await page.locator("text=Trigger").first().dragTo(canvas, { targetPosition: { x: 100, y: 200 } });
  76  |     await page.waitForTimeout(500);
  77  |     // Verify undo button exists and is enabled
  78  |     const undoBtn = page.locator("button[title*='Undo']");
  79  |     await expect(undoBtn).toBeVisible();
  80  |     // Undo
  81  |     await page.keyboard.press("Control+z");
  82  |     await page.waitForTimeout(500);
  83  |     // Verify redo button exists
  84  |     const redoBtn = page.locator("button[title*='Redo']");
  85  |     await expect(redoBtn).toBeVisible();
  86  |     // Redo
  87  |     await page.keyboard.press("Control+Shift+z");
  88  |     await page.waitForTimeout(500);
  89  |     await expect(undoBtn).toBeVisible();
  90  |     await page.screenshot({ path: "e2e/screens/06-undo-redo.png" });
  91  |   });
  92  | 
  93  |   test("07 - Template Gallery loads with templates", async ({ page }) => {
  94  |     await page.locator("text=Templates").first().click();
  95  |     await page.waitForTimeout(3000);
  96  |     await expect(page.locator("text=Research Assistant")).toBeVisible();
  97  |     await expect(page.locator("text=Content Writer")).toBeVisible();
  98  |     await expect(page.locator("text=Code Reviewer")).toBeVisible();
  99  |     await page.screenshot({ path: "e2e/screens/07-template-gallery.png" });
  100 |     await page.locator("text=Canvas").first().click();
  101 |   });
  102 | 
  103 |   test("08 - Connection status indicator is visible", async ({ page }) => {
  104 |     await expect(
  105 |       page.locator("text=Connecting to sidecar").or(
  106 |         page.locator("text=Connected").or(
  107 |           page.locator("text=Reconnecting")
  108 |         )
  109 |       ).first()
  110 |     ).toBeVisible();
  111 |     await page.screenshot({ path: "e2e/screens/08-connection-status.png" });
  112 |   });
  113 | 
  114 |   test("09 - Bottom panel tabs work", async ({ page }) => {
  115 |     await expect(page.locator("text=Run Log").first()).toBeVisible();
  116 |     await expect(page.locator("text=History").first()).toBeVisible();
  117 |     await expect(page.locator("text=Debug").first()).toBeVisible();
  118 |     await expect(page.locator("text=Version History").first()).toBeVisible();
  119 |     // Click Debug tab
  120 |     await page.locator("text=Debug").first().click();
  121 |     await page.waitForTimeout(1000);
  122 |     // Debug tab should show RunHistoryPanel
  123 |     const hasDebugContent = await page.locator("text=Run History").or(page.locator("text=No runs yet").or(page.locator("text=debug"))).first().isVisible().catch(() => false);
  124 |     // Click Version History tab
  125 |     await page.locator("text=Version History").first().click();
  126 |     await page.waitForTimeout(1000);
  127 |     // Version History panel should be visible
  128 |     const hasVersionContent = await page.locator("text=Version").or(page.locator("text=Snapshot").or(page.locator("text=history"))).first().isVisible().catch(() => false);
  129 |     await page.screenshot({ path: "e2e/screens/09-bottom-panel.png" });
  130 |   });
  131 | 
  132 |   test("10 - Workflow list and creation", async ({ page }) => {
  133 |     await page.waitForTimeout(2000);
  134 |     await expect(page.locator("text=Workflows").first()).toBeVisible();
> 135 |     await expect(page.locator("text=Execution Mode").first()).toBeVisible();
      |                                                               ^ Error: expect(locator).toBeVisible() failed
  136 |     await page.screenshot({ path: "e2e/screens/10-workflow-list.png" });
  137 |   });
  138 | 
  139 |   test("11 - Full workflow creation: Trigger → Agent → Output", async ({ page }) => {
  140 |     await page.waitForTimeout(2000);
  141 |     const canvas = page.locator(".react-flow");
  142 |     await page.locator("text=Trigger").first().dragTo(canvas, { targetPosition: { x: 80, y: 250 } });
  143 |     await page.waitForTimeout(300);
  144 |     await page.locator("text=Agent").first().dragTo(canvas, { targetPosition: { x: 350, y: 250 } });
  145 |     await page.waitForTimeout(300);
  146 |     await page.locator("text=Output").first().dragTo(canvas, { targetPosition: { x: 620, y: 250 } });
  147 |     await page.waitForTimeout(300);
  148 |     await expect(page.locator("text=Trigger").last()).toBeVisible();
  149 |     await expect(page.locator("text=Agent").last()).toBeVisible();
  150 |     await expect(page.locator("text=Output").last()).toBeVisible();
  151 |     await page.screenshot({ path: "e2e/screens/11-complete-workflow.png" });
  152 |   });
  153 | 
  154 |   test("12 - Validation shows errors for incomplete workflow", async ({ page }) => {
  155 |     await page.waitForTimeout(2000);
  156 |     const canvas = page.locator(".react-flow");
  157 |     await page.locator("text=Agent").first().dragTo(canvas, { targetPosition: { x: 300, y: 200 } });
  158 |     await page.waitForTimeout(1500);
  159 |     // Validation should detect missing trigger, missing output, missing model
  160 |     const hasValidation = await page.locator("text=error").or(page.locator("text=warning").or(page.locator("text=missing"))).first().isVisible().catch(() => false);
  161 |     if (hasValidation) {
  162 |       await expect(page.locator("text=error").or(page.locator("text=warning").or(page.locator("text=missing"))).first()).toBeVisible();
  163 |     }
  164 |     await page.screenshot({ path: "e2e/screens/12-validation-errors.png" });
  165 |   });
  166 | 
  167 |   test("13 - Cost Dashboard loads", async ({ page }) => {
  168 |     await page.locator("text=Cost").first().click();
  169 |     await page.waitForTimeout(500);
  170 |     await expect(page.locator("text=Cost").first()).toBeVisible();
  171 |     await page.screenshot({ path: "e2e/screens/13-cost-dashboard.png" });
  172 |     await page.locator("text=Canvas").first().click();
  173 |   });
  174 | 
  175 |   test("14 - Keyboard shortcuts work", async ({ page }) => {
  176 |     await page.waitForTimeout(2000);
  177 |     await page.keyboard.press("Control+p");
  178 |     await page.waitForTimeout(1000);
  179 |     // Properties panel may or may not be visible depending on state
  180 |     await page.keyboard.press("Control+k");
  181 |     await page.waitForTimeout(1500);
  182 |     // Command palette should be visible
  183 |     const hasPalette = await page.locator("text=Type a command or search").isVisible().catch(() => false);
  184 |     if (hasPalette) {
  185 |       await expect(page.locator("text=Type a command or search")).toBeVisible();
  186 |     }
  187 |     await page.keyboard.press("Escape");
  188 |     await page.screenshot({ path: "e2e/screens/14-keyboard-shortcuts.png" });
  189 |   });
  190 | 
  191 |   test("15 - Notification bell is visible", async ({ page }) => {
  192 |     await page.waitForTimeout(2000);
  193 |     await expect(page.locator("button[title='Notifications']")).toBeVisible();
  194 |     await page.screenshot({ path: "e2e/screens/15-notification-bell.png" });
  195 |   });
  196 | });
  197 | 
```