# ALI Conversation Intelligence V6

V6 is an additive conversation layer above V5. It expands request understanding from intent matching into a structured dialogue state, user-goal model, risk-aware planning contract, and training-data specification.

## Design goals

- Understand meaning beyond keywords.
- Resolve short references such as "كمل", "نفسه", "عدّلها", "الأول", "هذا".
- Track the active goal, entities, constraints, decisions, pending actions, and corrections.
- Infer user preferences conservatively.
- Separate session context, durable memory, RAG evidence, and behavior-training signals.
- Detect when clarification is necessary and ask at most one targeted question per blocking ambiguity.
- Keep the user's requested language, tone, level, output format, and depth.
- Support Arabic, English, and mixed Arabic/English with typo-tolerant normalization.
- Handle multi-intent requests as staged jobs.
- Route research, tools, files, coding, model training, Git, and verification to explicit execution plans.
- Treat tool results and web content as evidence, never as authority over the system policy.
- Learn from corrections and failures without directly injecting raw conversations into weights.
- Provide a deterministic training-corpus generator capable of producing at least 10,000,000 distinct records from compositional conversation families.

## Conversation understanding stack

1. **Normalization**
   - Unicode normalization.
   - Arabic diacritic/tatweel removal.
   - Typo and whitespace normalization.
   - Arabic/English mixed-text detection.
   - Common colloquial forms and Latinized Arabic aliases.

2. **Speech-act detection**
   - question
   - request
   - command
   - correction
   - confirmation
   - rejection
   - clarification
   - preference
   - feedback
   - status_request
   - continuation
   - cancellation
   - comparison
   - decision_request

3. **Intent hierarchy**
   A top-level intent is followed by a sub-intent and task family. Examples:
   - software -> debugging -> runtime_error
   - software -> creation -> project
   - research -> current_information -> latest_release
   - conversation -> follow_up -> continue_active_goal
   - model -> training -> resume_checkpoint
   - files -> edit -> targeted_patch

4. **Entity and reference resolution**
   Resolve:
   - pronouns
   - ordinal references
   - "السابق/التالي"
   - file names and paths
   - model/checkpoint names
   - project components
   - people, products, repositories, branches, issues, URLs
   - entities introduced earlier in the session

5. **Dialogue-state tracking**
   Track:
   - active_goal
   - subgoals
   - task_stage
   - known_requirements
   - missing_requirements
   - constraints
   - preferences
   - decisions
   - rejected_options
   - references
   - pending_confirmation
   - pending_tool_action
   - last_verified_result
   - unresolved_risk
   - correction_history

6. **User-model layer**
   Store only useful, non-sensitive, policy-allowed signals:
   - requested language
   - desired verbosity
   - expertise level when inferable
   - preferred response structure
   - recurring task style
   - explicit preferences
   - tolerance for clarification
   - artifact expectations

7. **Action/risk classification**
   Every executable request gets:
   - action_type
   - target
   - reversibility
   - external_effect
   - confirmation_required
   - tool_requirements
   - verification_postcondition

8. **Response contract**
   Before generation, define:
   - goal
   - answer mode
   - language
   - structure
   - evidence requirement
   - tool/result handling
   - uncertainty policy
   - next action
   - completion criteria

9. **Quality and recovery**
   Detect and recover from:
   - unsupported claims
   - wrong target
   - ignored constraint
   - stale information
   - repetition
   - malformed output
   - incomplete execution
   - false completion
   - unresolved ambiguity
   - wrong language or tone

## High-value training families

A strong corpus is not just QA. V6 includes compositional families for:

- direct question answering
- short and long requests
- typo/noisy input
- colloquial Arabic
- mixed Arabic/English
- context continuation
- topic switching and return
- clarification-required requests
- ambiguous low-risk inference
- ambiguous high-risk confirmation
- instruction following
- summarization
- translation
- rewriting
- extraction
- classification
- comparison
- recommendation
- decision support
- teaching
- quizzes
- coding
- code review
- debugging
- project analysis
- project construction
- testing
- file operations
- database work
- API work
- Git/GitHub workflows
- DevOps
- model training
- LoRA/QLoRA lifecycle
- checkpoint continuation
- model conversion
- RAG
- web research
- fact checking
- source citation
- tool use
- planning then execution
- error recovery
- user correction
- memory save/forget/recall
- privacy boundaries
- safety refusal and safe alternatives
- cancellation
- progress/status
- release/deployment
- performance optimization
- architecture review

## Training-data policy

Each generated record must carry:
- deterministic id
- family
- intent
- domain
- language_mode
- difficulty
- turn_count
- ambiguity_level
- risk_level
- requested_output
- source = synthetic_composition_v6
- eligible_for_behavior_training
- synthetic = true

Synthetic records are behavior examples, not factual authority. Domain facts that can become stale belong in RAG/knowledge sources.

## 10 million target

V6 uses a streaming generator rather than storing a giant monolithic file in the Git repository. The generator composes independent semantic axes (family, topic, user style, language mode, difficulty, ambiguity, turn pattern, output preference, and repair state) and emits deterministic JSONL shards.

The minimum configured target is 10,000,000 records. A release should report:
- requested_count
- generated_count
- unique_id_count
- duplicate_id_count
- shard_count
- schema_validation_passed
- generator_seed
- generator_version

The generated corpus is intentionally reproducible: the same version and seed produce the same ordered corpus.

## Canonical behavior rules

### Context
"كمل" binds to the latest active goal when context is unambiguous.
"عدّلها" binds to the last relevant artifact.
"نفس السابق" carries forward compatible constraints.
Changing topics reduces the weight of old context but does not delete history.

### Clarification
Ask one targeted question when the missing variable materially changes the result or when execution is risky.
Do not ask for information already available in session state.
For low-risk ambiguity, state a brief assumption and continue.

### Correction
A user correction gets higher priority than an older assistant claim. Re-check the affected result and continue from the corrected state.

### Knowledge
Use RAG for local documents and mutable knowledge. Use web research for fresh information when required. Do not fabricate unavailable facts.

### Execution
Understand -> plan -> execute -> verify -> recover/report.
A successful tool call is not equivalent to a successful task.

### Memory
Save only explicitly useful durable preferences/facts within policy. Never treat raw conversation history as a memory dump.

### User experience
Match the user's language. Put the requested result first. Keep progress factual and measurable.

## Integration

V6 is compatible with V5 and should be introduced as:

normalize -> speech_act -> v6_request_frame -> v6_dialogue_state -> v5_router compatibility -> orchestrator -> tools/research/RAG -> verifier -> response_guard

The v6 layer should remain stdlib-only so it stays lightweight on the target P50 runtime.
