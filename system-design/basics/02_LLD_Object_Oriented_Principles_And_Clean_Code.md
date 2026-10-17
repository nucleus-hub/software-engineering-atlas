# LLD: Object-Oriented Principles & Clean Code

> A visual guide to designing classes that survive the next requirement. Use it to structure a low-level design round, choose boundaries from the changes you expect, defend each abstraction, and spot the smells that make change expensive.

---

## 1. One-page visual summary

![Six-stage low-level design interview framework](assets/topic-02/lld_interview_framework.png)

The low-level design round is the same narrowing funnel as system design, one zoom level down: find the use cases, name the objects that own them, fix their contracts, connect them, write the core path, and then prove the design absorbs a change.

| Phase | Time | Deliverable | On the whiteboard before moving on |
|---|---:|---|---|
| Clarify | 0–5 min | Use cases, actors, scope, likely changes | 3–4 use cases, an out-of-scope list, 1–2 named "likely changes" |
| Model | 5–12 min | Entities and their responsibilities | Each class with a one-sentence responsibility |
| Contract | 12–18 min | Interfaces, invariants, error semantics | 2–4 interfaces and the rules each object guarantees |
| Relate | 18–25 min | Class diagram: has-a, is-a, depends-on | One diagram where every arrow is justified |
| Code | 25–38 min | The core flow in real code | The happy path plus one failure path |
| Extend | 38–45 min | A change scenario and its test | "Adding X touches only Y" and the test that proves it |

**Machine-coding rounds (60–90 min):** the extra time goes into *Code* and running tests. Clarify and Model should not grow. A sprawling class diagram with no code reads as avoidance.

![Five SOLID principles framed as questions about change](assets/topic-02/solid_principles.png)

| Principle | Question to ask | Smell in code review | What healthy looks like |
|---|---|---|---|
| **S** — Single Responsibility | Which person or team asks for this class to change? | One class gets edited for finance, operations, and UX reasons. | The class has one cohesive reason to change. |
| **O** — Open/Closed | Can a new case be added as a new class, without editing tested code? | A `switch` on a type code grows every sprint. | New cases plug in at a deliberate extension point, and tested code stays untouched. |
| **L** — Liskov Substitution | Can every subtype stand in for its base type without surprising callers? | Overrides throw, silently do nothing, or demand more from callers. | Subtypes demand no more and promise no less than their base type. |
| **I** — Interface Segregation | Does each client use everything in the interface it depends on? | Implementations stub out methods by throwing `UnsupportedOperationException`. | Interfaces are small and shaped around what each client actually calls. |
| **D** — Dependency Inversion | Can the business logic run, and be tested, without real infrastructure? | A service creates its own database client with `new MySqlRepo()`. | The business logic owns the interface, and infrastructure plugs in behind it. |

!!! tip "The LLD round in one sentence"
    Find the likely changes, give each one a single owner behind a small contract, and prove that a new requirement becomes a new class rather than an edit.

---

## 2. Core mental model

### Design around change and invariants

An object owns **state plus the behavior that keeps that state valid**. An **invariant** is a rule that must always hold: a balance never goes negative, an order always has at least one line. A boundary earns its place when it contains one cohesive policy and stops unrelated changes from spreading.

```text
Useful boundary = cohesive responsibility + protected invariant + explicit contract
Design quality  = cost of a likely change × confidence that behavior is still correct
```

The second line is the only test that matters: when a likely change arrives, how many classes must you edit, and will a test tell you if you broke something?

![Object design flow from encapsulation to local evolution](assets/topic-02/oop_mental_model.png)

### Coupling and cohesion: the two dials

Every principle in this guide tunes one of two dials. **Cohesion** measures how strongly the things inside a module belong together: do they change for the same reason? **Coupling** measures how much one module knows about another: does a change here force a change there?

![Quadrant of coupling against cohesion with the modular quadrant as the goal](assets/topic-02/coupling_cohesion.png)

Not all coupling is equal. From worst to most acceptable:

| Coupling kind | What it looks like | Why it matters |
|---|---|---|
| Content | One class reaches directly into another class's fields or internals. | Any internal refactor in the other class breaks yours. |
| Global | Classes share mutable static state, or singletons that hold state. | Dependencies are hidden, and tests pass or fail depending on the order they run in. |
| Control | A caller passes a boolean or enum that tells the callee *what to do*. | The caller has to know how the callee works inside. |
| Stamp | A method receives a whole `Order` when it only needs the `orderId`. | Changes to fields the method never uses still ripple out to it. |
| Data | A method receives exactly the values it needs, and nothing more. | This is the goal: the narrowest contract that is still honest. |

### Tell, don't ask

Push behavior to the object that owns the data instead of pulling the data out to decide elsewhere. A chain of getters is coupling you can see:

```java
// Ask: the caller knows customers have wallets, and how wallets are debited
order.getCustomer().getWallet().debit(order.total());

// Tell: the order owns the rule; the caller states intent
order.chargeCustomer();
```

This is the **Law of Demeter**: talk to your immediate collaborators, not to their collaborators. Fluent builders and streams are fine, because each call returns the same abstraction.

---

## 3. The four pillars, done right

| Pillar | What it buys you | The misuse that costs points |
|---|---|---|
| **Encapsulation** | Each invariant is enforced in exactly one place, by the object that owns the data. | Making fields private, then adding a public setter for every one of them. |
| **Abstraction** | Callers depend on *what* an object does, not *how* it does it. | Hiding something the caller needs in order to decide, such as cost, latency, or blocking behavior. |
| **Inheritance** | Subtypes reuse a true, stable is-a contract from their parent. | Inheriting just to reuse code, or building deep hierarchies. |
| **Polymorphism** | Behavior varies by type without callers needing `if` or `switch` statements. | Creating an interface that will only ever have one implementation. |

### Encapsulation: the rule lives with the data

```java
// Bad: the invariant lives nowhere, so every caller invents its own version
class BankAccount { public Money balance; }
account.balance = account.balance.minus(amount);      // nothing stops a negative balance

// Good: one owner, one rule
final class BankAccount {
    private Money balance = Money.ZERO;

    void withdraw(Money amount) {
        if (amount.isGreaterThan(balance)) throw new InsufficientFundsException(balance, amount);
        balance = balance.minus(amount);
    }
    Money balance() { return balance; }               // read access, never write access
}
```

Go one step further with **value objects**: make invalid states unrepresentable, so validation happens once, at construction, instead of in every caller.

```java
record EmailAddress(String value) {
    EmailAddress {
        if (value == null || !value.contains("@")) throw new IllegalArgumentException("invalid email");
    }
}
// A method taking EmailAddress never re-validates. A String could be anything.
```

**Careful:** a private field with a public setter is not encapsulation. It is a public field with extra steps.

### Abstraction: hide the how, not the decision

```java
// Bad: every caller depends on SMTP mechanics, in the right order
smtp.connect(host, 587); smtp.authenticate(user, password);
smtp.send(to, subject, body); smtp.disconnect();

// Good: the contract is the intent
interface Sender { SendResult send(Notification notification); }
```

A good abstraction hides **irrelevant** detail. It must not hide what the caller needs in order to decide: if `send` can block for 30 seconds or costs money per call, that belongs in the contract (a timeout, a result type, an honest name). The opposite failure is a **leaky abstraction**, where callers end up catching `SMTPException` anyway.

### Inheritance: only for an is-a that keeps every promise

Inheritance couples the child to the parent's **implementation**, not just its interface. The classic demonstration, from *Effective Java*:

```java
class InstrumentedHashSet<E> extends HashSet<E> {
    int addCount = 0;
    @Override public boolean add(E e) { addCount++; return super.add(e); }
    @Override public boolean addAll(Collection<? extends E> c) { addCount += c.size(); return super.addAll(c); }
}
// addAll(List.of("a", "b", "c")) leaves addCount == 6, not 3
```

`HashSet` inherits an `addAll` that calls `add` for each element, so every item is counted twice. Nothing in the documented interface says so: the subclass broke on a parent implementation detail. This is the **fragile base class** problem, and it is why "favor composition over inheritance" exists.

Use inheritance when the hierarchy is shallow, stable, and every subtype honors the parent's full contract (template-method frameworks, sealed domain hierarchies). Otherwise, compose.

### Polymorphism: replace the type switch

```java
// Bad: every new channel edits this switch, and every other switch on Channel
switch (channel) {
    case EMAIL -> smtp.send(n);
    case SMS   -> smsGateway.send(n);
}

// Good: the variation lives behind one contract, chosen at wiring time
senders.get(channel).send(n);                          // Map<Channel, Sender>
```

**The senior nuance: a switch is not always wrong.** This is the *expression problem*. Polymorphism makes adding **types** cheap and adding **operations** expensive; a switch over a closed set does the reverse. With sealed types (Java 17) and pattern-matching `switch` (Java 21), an exhaustive switch is compiler-checked: add a variant, and every switch fails to compile until it handles it.

```java
sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

double area(Shape shape) {
    return switch (shape) {                            // no default: exhaustiveness is checked
        case Circle c -> Math.PI * c.r() * c.r();
        case Square s -> s.side() * s.side();
    };
}
```

Rule of thumb: an **open set of variants with rich behavior** calls for polymorphism. A **closed, stable set whose operations keep growing** calls for sealed types and exhaustive switches.

### Composition over inheritance

![Comparison of inheritance and composition for flight behavior](assets/topic-02/composition_vs_inheritance.png)

```java
interface FlyBehavior { void fly(); }

final class Bird {
    private final FlyBehavior flight;
    Bird(FlyBehavior flight) { this.flight = flight; }
    void fly() { flight.fly(); }
}
Bird sparrow = new Bird(new WingedFlight());
Bird penguin = new Bird(new NoFlight());               // no override, no exception
```

The contract of `fly()` is now "perform this bird's flight behavior", which honestly includes none. The same move fixes `InstrumentedHashSet`: wrap a `Set` and forward to it (a decorator), and the counter no longer depends on how `HashSet` implements `addAll`. The quick test: if you are about to override a method to throw or do nothing, the relationship was never is-a.

---

## 4. SOLID, as questions about change

The §1 table is the summary. Here each principle gets a realistic failure, the fix, and the trap.

### S — Single Responsibility: one actor, one reason to change

"A module should be responsible to one, and only one, actor." The question is not "does it do one thing?" but **"who asks for it to change?"**

```java
// Bad: finance (pay rules), the DBA (schema), and HR comms (email copy) all edit this class
class PayrollService {
    Money calculatePay(Employee e) { ... }
    void save(Paycheck p)          { ... }             // SQL
    void emailPayslip(Paycheck p)  { ... }             // templates + SMTP
}

// Good: one class per actor
final class PayCalculator      { Money calculatePay(Employee e) { ... } }
final class PaycheckRepository { void save(Paycheck p) { ... } }
final class PayslipMailer      { void send(Paycheck p) { ... } }
```

**Careful:** SRP is not "one method per class". Methods that protect the same invariant belong together; splitting them scatters one rule across files, which is the opposite of the goal.

### O — Open/Closed: new cases arrive as new classes

```java
// Bad: every new shipping rule reopens tested code
Money shippingCost(Order order) {
    if (order.isExpress()) return Money.of(15);
    if (order.total().isAbove(Money.of(50))) return Money.ZERO;
    return Money.of(5);
}

// Good: each rule is a class; the list is ordered by priority
interface ShippingRule { Optional<Money> costFor(Order order); }

Money shippingCost(Order order) {
    return rules.stream()
        .map(rule -> rule.costFor(order)).flatMap(Optional::stream)
        .findFirst().orElse(DEFAULT_COST);
}
```

**Careful:** "closed" applies to the axes of change you have evidence for. Adding a seam for a variation you have never seen is YAGNI, not OCP.

### L — Liskov Substitution: subtypes keep the base contract

Matching method signatures is the easy part; LSP is about **behavior**. A subtype must obey four rules:

| Rule | Meaning | Violation example |
|---|---|---|
| Preconditions | A subtype cannot **strengthen** what it requires from callers. | The base accepts any amount, but the subtype rejects amounts over 1,000. |
| Postconditions | A subtype cannot **weaken** what it promises to return. | The base guarantees a receipt, but the subtype returns `null`. |
| Invariants | A subtype must **preserve** every rule the base type keeps true. | `Square extends Rectangle` breaks the rule that width and height can change independently. |
| Exceptions | A subtype cannot add **new** ways to fail. | The base never throws on `refund`, but the subtype throws `UnsupportedOperationException`. |

The JDK has a famous case: `List.of(...)` returns a list whose `add()` throws. The Javadoc marks `add` as an *optional operation*, which keeps it technically legal and moves the failure from compile time to production. A senior answer names this as a deliberate trade-off (one `List` type instead of a mutable/immutable split), not a model to copy.

```java
// Bad: a refund-capable base type with a subtype that cannot refund
class PaymentMethod { Receipt charge(Money m) { ... }  Receipt refund(Money m) { ... } }
class GiftCard extends PaymentMethod {
    @Override Receipt refund(Money m) { throw new UnsupportedOperationException(); }
}

// Good: model each capability honestly
interface Chargeable { Receipt charge(Money amount); }
interface Refundable { Receipt refund(Money amount); }
final class CreditCard implements Chargeable, Refundable { ... }
final class GiftCard   implements Chargeable { ... }
```

**How to prove it:** write one contract test against the base type and run it against every implementation (§8).

### I — Interface Segregation: interfaces shaped by their clients

```java
// Bad: every implementation must support checkout, analytics, and ops needs
interface CustomerRepository {
    Customer findById(CustomerId id);
    void save(Customer customer);
    Report monthlyRevenueReport();                     // the analytics team's need
    void purgeInactive(Duration olderThan);            // the ops team's need
}

// Good: role interfaces, one per kind of client
interface CustomerReader    { Customer findById(CustomerId id); }
interface CustomerWriter    { void save(Customer customer); }
interface CustomerReporting { Report monthlyRevenueReport(); }
```

One class may still implement several of them. The point is that **each client depends only on what it calls**, so checkout code is not recompiled, or re-mocked, because analytics added a report. **Careful:** split by client need, not by method; one-method interfaces for everything is *interface confetti*.

### D — Dependency Inversion: policy owns the interface

![Dependency inversion: before, policy depends on MySQL; after, both adapters depend on a policy-owned interface](assets/topic-02/dependency_inversion.png)

```java
// Bad: business policy constructs infrastructure
class OrderService {
    private final MySqlOrderRepo repo = new MySqlOrderRepo();     // welded to MySQL
}

// Good: the interface lives in the policy's package; details implement it
interface OrderRepository { Optional<Order> find(OrderId id); void save(Order order); }

final class OrderService {
    private final OrderRepository orders;
    OrderService(OrderRepository orders) { this.orders = orders; }   // injected
}
```

Interviewers probe two things. **Ownership:** the interface belongs to the high-level module and is shaped by its needs (`find`, `save`), not by what MySQL offers; an interface that mirrors the driver is indirection, not inversion. **Inversion is not injection:** DI is one way to wire the design, and a Spring container full of concrete classes is still concrete coupling.

---

## 5. Clean code: DRY, KISS, YAGNI

![DRY, KISS, and YAGNI pulling from opposite ends of the abstraction spectrum](assets/topic-02/clean_code_guardrails.png)

SOLID decides where responsibilities go; these three decide **how much** abstraction to build. They pull in opposite directions, and that tension is the point.

| Rule | Guards against | Apply it when | Misuse to avoid |
|---|---|---|---|
| **DRY** — Don't Repeat Yourself | One business rule having several sources of truth that drift apart. | The same *knowledge* (a rule, a rate, a format) is written in more than one place. | Merging code that only looks alike but belongs to different owners. |
| **KISS** — Keep It Simple | Accidental complexity that the requirements never asked for. | A layer or mechanism does not buy any capability you actually need. | Oversimplifying domain rules that are genuinely complex, such as tax or pricing. |
| **YAGNI** — You Aren't Gonna Need It | Building features and abstractions for a future that may never come. | There is no current evidence that the variation will happen. | Refusing a cheap, obvious seam, such as an interface in front of a third-party API. |

### DRY is about knowledge, not text

```java
// Two copies of one rule: when the GST rate changes, one will be missed
class Checkout      { Money tax(Money subtotal) { return subtotal.times(0.18); } }
class RefundService { Money tax(Money subtotal) { return subtotal.times(0.18); } }

// One owner
final class TaxPolicy { Money taxOn(Money subtotal, Region region) { ... } }
```

The reverse mistake is just as common. Two validation methods that look identical today but belong to different actors (signup and KYC) should stay separate: merge them, and the first divergent requirement adds a boolean flag, then another. "Duplication is far cheaper than the wrong abstraction" (Sandi Metz). The **rule of three** is the practical tie-breaker: tolerate the second copy, abstract on the third.

### KISS: complexity must buy something

```java
// Three channels in one repository, so... a plugin framework with discovery and priorities
ServiceLoader.load(SenderPlugin.class).stream().sorted(byPriority()).forEach(registry::register);

// What the requirement actually needs
Map<Channel, Sender> senders = Map.of(EMAIL, emailSender, SMS, smsSender, PUSH, pushSender);
```

KISS removes *accidental* complexity. Tax law, retry semantics, and pricing tiers are *essential* complexity; flattening them into something that looks clean but gets edge cases wrong is a bug, not simplicity.

### YAGNI: leave the seam, not the scaffolding

One `PaymentGateway` interface with a single `StripeGateway` behind it costs one file and keeps checkout tests independent of Stripe. Writing `PaypalGateway` and `RazorpayGateway` stubs "for later" means coding against guessed APIs that will be wrong on the day they are needed. §6 shows how to defend exactly this decision.

### Code-level signals interviewers notice

| Signal | Prefer | Avoid |
|---|---|---|
| Names | Names that state intent, such as `ReservationExpiryPolicy` or `isEligibleForRefund()`. | Vague names such as `Manager`, `Helper`, `Util`, `data`, or `flag`. |
| Functions | Short functions at one level of abstraction, with guard clauses first. | 80-line methods that mix business rules with I/O. |
| Arguments | Value objects such as `Money` and `OrderId`. | Boolean flag parameters, and raw strings or numbers for domain concepts (primitive obsession). |
| State | Immutable objects by default, using `final` fields and records. | A setter for every field, or mutable state shared between objects. |
| Errors | Typed results or specific exceptions that callers can act on. | Empty `catch (Exception e) {}` blocks, or returning `null` to mean "not found". |
| Comments | Comments that explain *why* a decision was made. | Comments that repeat *what* the next line does. |

---

## 6. Decision and trade-off tables

!!! abstract "The decision template: memorize this"
    Given **likely change X**, choose **A** over **B** because it keeps that change **local to C**. It costs **D**. Validate it with **test E**, and revisit when **F** happens.

Two worked instances:

> Given **new channels arriving every quarter**, choose **a `Sender` interface with one adapter per channel** over **a `switch` in the service** because a new channel becomes **one new class plus one wiring line**. It costs **an interface, a registry, and indirection when debugging**. Validate with **a shared contract test every adapter must pass**. Revisit if **channels need different workflows**, not just different transports.

> Given **one payment provider and no second one signed**, choose **a concrete `StripeGateway` behind a narrow `PaymentGateway` port** over **a multi-provider plugin framework** because it **keeps the code honest to the one real API**. It costs **a refactor when provider two arrives**. Validate with **checkout tests against a fake gateway**. Revisit when **a second provider is contracted**.

### Composition or inheritance?

| Question | Prefer composition | Consider inheritance |
|---|---|---|
| Relationship | The object **has** a capability that could be replaced. | The subtype truly **is** the base type, in every behavior. |
| Variation | The behavior changes independently, or needs to change at runtime. | The hierarchy is stable and shallow, two levels at most. |
| Reuse goal | You want to reuse a capability across unrelated classes. | You want subtypes to share a true invariant and contract. |
| Main risk | More objects to create and wire together. | A fragile base class: every subtype depends on the parent's internals. |
| How to test | Swap in a fake implementation of the capability. | Run the base type's contract tests against every subtype. |

### Add an abstraction?

| Evidence | Decision | Optimizes for | Cost |
|---|---|---|---|
| You already have two or more real implementations. | Extract a shared interface (a contract). | Substitution, and adding new cases without editing old code. | One more level of indirection to read through. |
| There is one implementation, but it does I/O or wraps a third party. | Put a narrow interface (a port) in front of it. | Testing with fakes, and isolating your code from the vendor. | One extra type to maintain. |
| There is one stable implementation that runs in-process. | Keep it as a concrete class. | Readability. | Extracting an interface later, if change actually arrives. |
| Variants change every week. | Use a strategy, or an ordered list of rules. | Adding a variant without touching existing ones. | Rules for how variants are discovered and ordered. |
| The only reason is a hypothetical future. | Defer the abstraction. | YAGNI: no code written for guesses. | A refactor when real evidence appears. |

---

## 7. Design smells & refactoring

![Design smells connected to expensive change](assets/topic-02/design_smells.png)

| Smell (principle at stake) | How you spot it in review | How to fix it | What the fix can break |
|---|---|---|---|
| **God class** (SRP) | The class is edited in most pull requests, and its name often ends in `Manager`. | Extract one class per actor that asks for changes. | Splitting one invariant across several classes, so nobody owns it. |
| **Shotgun surgery** (DRY) | Changing one rule means touching five or more files. | Move that knowledge into a single owner. | Merging code that was only coincidentally similar. |
| **Type switch** (OCP) | The same `switch` or `instanceof` check appears in several places. | Replace the conditional with polymorphism. | Adding an interface for a closed, stable set that a sealed switch would handle better. |
| **Refused bequest** (LSP) | Subclasses override inherited methods to throw or do nothing. | Split the hierarchy, and compose capabilities instead. | Many small types that all need wiring. |
| **Fat interface** (ISP) | Implementations stub out methods they cannot support. | Split it into role interfaces, one per kind of client. | Interface confetti: dozens of one-method interfaces. |
| **Concrete coupling** (DIP) | Business logic creates infrastructure directly with `new`. | Inject an interface owned by the business logic. | An interface that just mirrors the database driver, which is indirection, not inversion. |
| **Feature envy** (Encapsulation) | A method uses another class's getters more than its own fields. | Move the method to the class that owns the data. | Moving behavior into the wrong class. |
| **Primitive obsession** (Encapsulation) | Raw types like `String email` and `long amountInCents` appear everywhere. | Introduce value objects that validate themselves. | Wrapping values that have no rules, which adds types for nothing. |
| **Service locator** (DIP) | Methods fetch dependencies from a global registry halfway through. | Use constructor injection, so the signature shows every dependency. | Constructors with many parameters, which often hints at an SRP problem. |

!!! warning "Refactor from evidence, not taste"
    Name the change that hurt (or will), measure its blast radius, and make the smallest boundary move that contains it. "This could be cleaner" is not a reason. "This rule changed three times and we missed a copy twice" is.

---

## 8. Worked example: notification service

**Prompt:** "Design the classes for a service that notifies users about order events by email, SMS, or push."

### Questions to ask before designing anything

| Question | Why it matters | Assumed answer |
|---|---|---|
| Which channels are needed now, and which are coming next? | It decides whether a channel extension point is backed by evidence. | Email, SMS, and push now; WhatsApp is planned. |
| Can users opt out per channel, or set quiet hours? | It decides whether preferences need their own policy class. | Yes, both. |
| What should happen when a provider fails? | Retry rules shape the `Sender` contract. | Retry temporary failures, and stop on permanent ones. |
| Must each notification be delivered at most once? | It means the model needs an idempotency key. | Yes: users must never get duplicate texts on a retry. |
| Is sending synchronous to the caller, or queued? | It decides where retries and latency are handled. | A queue worker calls the service, so a send may take a few seconds. |

**Scope.** *In:* route an order event to each channel the user allows, render the content, deliver it, retry transient failures, and report a per-channel outcome. *Out:* the queue itself, scheduling, analytics, and template authoring.

### Classes and responsibilities

| Class | Responsibility | Changes when | Principle at work |
|---|---|---|---|
| `Notification` (record) | Holds a valid message: recipient, channel, body, and idempotency key. | The message fields change. | Encapsulation: it validates itself on construction. |
| `Sender` (interface) | Delivers one notification and classifies the outcome. | Rarely: it is the stable contract everything depends on. | ISP and DIP: it is small, and owned by the policy side. |
| `EmailSender`, `SmsSender`, `PushSender` | Each one speaks a single provider's API. | That provider's API or terms change. | OCP and SRP: a new provider is a new class. |
| `PreferencePolicy` | Decides which channels a user allows right now. | Product rules about opt-outs or quiet hours change. | SRP: preference rules live in one place. |
| `RetryPolicy` | Decides whether to retry a failed send, and when. | Reliability settings are tuned. | Composition: it is plugged into the service, not inherited. |
| `NotificationService` | Orchestrates the flow: pick channels, render, send, and collect results. | The workflow itself changes. | SRP: it coordinates, but holds no channel or retry logic. |

### Contracts

```java
record Notification(UserId to, Channel channel, String body, String idempotencyKey) {
    Notification {
        Objects.requireNonNull(to, "to"); Objects.requireNonNull(channel, "channel");
        if (body == null || body.isBlank()) throw new IllegalArgumentException("empty body");
    }
}

sealed interface SendResult permits Delivered, RetryableFailure, PermanentFailure {}
record Delivered(String providerMessageId) implements SendResult {}
record RetryableFailure(String reason)    implements SendResult {}   // timeout, 503, throttled
record PermanentFailure(String reason)    implements SendResult {}   // invalid number, blocked

interface Sender {
    Channel channel();
    SendResult send(Notification notification);   // classifies provider errors; never throws them
}
```

Why a sealed result instead of exceptions? Retry logic depends on the **classification**, and the compiler now forces every caller to handle all three outcomes. That classification is part of the `Sender` contract: an adapter that returns `PermanentFailure` for a timeout breaks substitution, even though it compiles.

![Notification service class diagram with policy above and channel adapters below a boundary](assets/topic-02/notification_architecture.png)

### Core flow

```java
final class NotificationService {
    private final Map<Channel, Sender> senders;     // toMap(Sender::channel, s -> s) over injected adapters
    private final PreferencePolicy preferences;
    private final TemplateRenderer renderer;
    private final RetryPolicy retry;
    private final Clock clock;                      // even time is a dependency
    // Constructor: all five collaborators are injected; nothing here calls `new`.

    Map<Channel, SendResult> notify(UserId user, OrderEvent event) {
        Map<Channel, SendResult> results = new EnumMap<>(Channel.class);
        for (Channel channel : preferences.allowedChannels(user, clock.instant())) {
            Notification notification = renderer.render(user, channel, event);
            Sender sender = senders.get(channel);
            results.put(channel, retry.execute(() -> sender.send(notification)));
        }
        return results;
    }
}
```

Three details worth saying out loud. Building the map with `toMap` throws at startup if two adapters claim the same channel, so a wiring bug fails fast instead of at 2 a.m. The injected `Clock` makes quiet-hours logic testable without waiting for 22:00. And `RetryPolicy` retries only `RetryableFailure`, which is safe because the idempotency key lets providers drop duplicates.

### Change walkthrough

| Change request | What you edit | What you add | What stays untouched |
|---|---|---|---|
| Add WhatsApp as a channel. | One wiring line that registers the new sender. | A `WhatsAppSender` class. | The service, both policies, and every other adapter. |
| Add quiet hours from 22:00 to 07:00. | `PreferencePolicy`. | Tests for the new rule. | The service and all the adapters. |
| Switch to a different SMS provider. | The wiring that picks the SMS sender. | A `TwilioSmsSender` class. | Everything else. |
| Use exponential backoff for retries. | `RetryPolicy`. | Nothing. | Everything else. |
| Send a daily digest instead of instant messages. | `NotificationService`, because the workflow itself changes. | A `DigestScheduler` class. | The adapters and their contract. |

The last row matters. A digest is a **workflow** change, and the orchestrator is supposed to change for workflow reasons. OCP protects the axes you anticipated, not every possible change, and saying so is a stronger answer than claiming the design is closed to everything.

### Proving substitution: contract tests

```java
abstract class SenderContractTest {
    protected abstract Sender sender();                 // each adapter's test supplies one
    protected abstract void providerTimesOut();
    protected abstract void providerRejectsRecipient();

    @Test void timeoutIsRetryable() {
        providerTimesOut();
        assertInstanceOf(RetryableFailure.class, sender().send(sampleNotification()));
    }
    @Test void invalidRecipientIsPermanent() {
        providerRejectsRecipient();
        assertInstanceOf(PermanentFailure.class, sender().send(sampleNotification()));
    }
}
class SmsSenderTest extends SenderContractTest { /* stubs the SMS gateway */ }
```

Every new adapter inherits the whole suite. This is where LSP stops being a slogan: substitution is verified, not assumed. (Inheritance is right here: every concrete test genuinely *is* a sender contract test.)

---

## 9. Anti-patterns that cost points

- Drawing a 20-class diagram before writing one line of the core flow.
- An interface for every class "for testability", each with exactly one implementation.
- `Manager`, `Processor`, and `Helper` classes holding most of the logic.
- Inheriting to reuse code (`class Stack extends ArrayList`).
- Getters and setters for every field, with the rules implemented in callers.
- Naming a pattern ("I'll use a Strategy here") without saying which change it absorbs.
- Claiming the design is "open to any future requirement".

---

## 10. Final revision checklist

```text
[ ] CLARIFY use cases, scope, and the 1–2 changes most likely to come
[ ] MODEL entities with one-sentence responsibilities and one actor each
[ ] PROTECT invariants inside objects; use value objects for validated data
[ ] CONTRACT small, client-shaped interfaces owned by the policy that uses them
[ ] SUBSTITUTE only when subtypes keep preconditions, postconditions, invariants, errors
[ ] COMPOSE capabilities; inherit only for a stable, shallow, honest is-a
[ ] EXTEND by showing a likely change become a new class, not an edit
[ ] RIGHT-SIZE: DRY for knowledge, KISS for mechanism, YAGNI for speculation
[ ] PROVE substitution with contract tests every implementation must pass
[ ] DEFEND each choice: change localized, cost, validation, revisit trigger
```

!!! success "The Staff-level finish"
    Summarize the core classes, name the change the design absorbs best, admit the change it does not absorb (and why that is acceptable), and show how a test proves every implementation keeps the contract.
