# LLD: Object-Oriented Principles & Clean Code

## Terms to know before you start

You do not need to memorize these. Come back to this table whenever a term feels unfamiliar.

| Term | What it means in plain words |
|---|---|
| **Class and object** | A class is a blueprint that describes data and the methods that work on it. An object is one concrete instance created from that blueprint. |
| **Interface** | A list of methods that a class promises to provide, without saying how. Code that uses an interface works with any class that implements it. |
| **Implementation** | A class that provides the actual code behind an interface. One interface can have many implementations. |
| **Caller (or client)** | The code that uses an object by calling its methods. |
| **Invariant** | A rule about an object's data that must always be true, such as "a short code is always exactly 7 characters long". |
| **Contract** | Everything a caller may rely on when using an object: its methods, what they accept, what they return, and how they fail. |
| **Dependency** | Something a class needs in order to do its job. If class A calls class B, then A depends on B. |
| **Wiring** | The code that creates objects and connects them to their dependencies, usually at application startup. |
| **Coupling** | How much one class knows about another. High coupling means a change in one class forces changes in others. |
| **Cohesion** | How closely the code inside one class belongs together. High cohesion means everything in the class serves one purpose. |
| **Refactoring** | Changing the structure of code without changing what it does, usually to make the next change easier. |
| **Test double (fake)** | A simple stand-in object used in tests instead of a real dependency, such as an in-memory link store that keeps links in a map instead of a real database. |

??? info "Java syntax used on this page (open if you learned Java before version 17)"
    - **`final class`** means the class cannot be extended by inheritance.
    - **`record`** is a short way to declare a class whose job is to hold data. `record Point(int x, int y) {}` automatically creates private final fields, a constructor, and the accessor methods `x()` and `y()`.
    - **`switch` with `->`** is the newer switch syntax. Each case runs only its own branch, so there is no `break` and no accidental fall-through.
    - **`List.of(...)`** and **`Map.of(...)`** create small collections that cannot be modified afterwards. **`List.copyOf(list)`** makes an unmodifiable copy of an existing list.
    - **`Optional<T>`** holds either one value or nothing. A method that returns `Optional.empty()` is saying "nothing was found", and the caller is forced to handle that case instead of receiving `null`.

---

## 1. The running example: one messy class

Every principle on this page is easier to understand when you watch it fix a real problem. So instead of using a different example for each idea, the whole page improves one piece of code step by step.

In **Basics 1**, you sized a URL shortener and drew its main boxes: an API, a cache, a database, and a queue for click events. This page zooms into the code inside the API box. Since launch, the product team has also added three link features: links that expire, links protected by a password, and links that only work in certain countries. Here is a first version of the redirect code that works, but that is painful to change:

```java
class LinkManager {
    public String code;                       // the create path fills these in, and anyone can set them to anything
    public String longUrl;
    public String type;                       // "STANDARD", "EXPIRING", "PASSWORD", or "COUNTRY_LOCKED"

    String redirect(String code, String password, String country) {
        String cached = redis.get("link:" + code);                                          // cache plumbing
        Row row = (cached != null) ? Row.fromJson(cached)
                : new PostgresClient(DB_URL).query("SELECT * FROM links WHERE code = ?", code); // SQL plumbing
        if (cached == null) redis.set("link:" + code, row.toJson());

        switch (row.type()) {                                                               // link-type rules
            case "EXPIRING"       -> { if (Instant.now().isAfter(row.expiresAt())) return "410 Gone"; }
            case "PASSWORD"       -> { if (!matches(password, row.passwordHash())) return "401 Unauthorized"; }
            case "COUNTRY_LOCKED" -> { if (!row.allowedCountries().contains(country)) return "403 Forbidden"; }
        }
        analytics.recordClick(code, country);                                               // click tracking
        return row.longUrl();
    }
}
```

This class has five separate problems, and each level below fixes one of them:

| Problem in `LinkManager` | Fixed in |
|---|---|
| Any caller can create a link with an invalid code, or with a dangerous URL such as `javascript:alert(1)`. | Level 1: Encapsulation |
| The redirect logic is buried under cache and SQL plumbing, and an unknown code is never handled. | Level 2: Abstraction |
| Every new link feature means editing the `switch`, and every other `switch` on the link type. | Level 3: Polymorphism |
| A link can only have one type, so a link that both expires and needs a password cannot exist. | Level 4: Composition over inheritance |
| The class knows about Redis, Postgres, link rules, and click tracking all at once. | Level 5: Coupling and cohesion |

---

## 2. The four pillars of object-oriented design

![Object design flow from encapsulation to local evolution](assets/topic-02/oop_mental_model.png)

The four pillars build on each other. Encapsulation protects data, abstraction hides details behind a simple interface, polymorphism lets many implementations share one interface, and composition assembles small objects into bigger behavior. Together they lead to the goal shown at the bottom of the diagram: when requirements change, only a small number of classes need to change.

### Level 1: Encapsulation, keeping the rules with the data

**Encapsulation** means an object keeps its data private and only exposes methods that keep that data valid. The rules about the data (its invariants) are enforced in exactly one place: inside the object that owns the data.

In `LinkManager`, the fields are public, so nothing stops a caller from setting `code = "abc"` (too short) or `longUrl = "javascript:alert(1)"`, a classic trick for running an attacker's script in a visitor's browser. Every caller would have to remember to validate the data, and sooner or later one of them would forget.

The fix is to make each object responsible for its own validity. It checks its data once, in the constructor, and never allows that data to change afterwards:

```java
record ShortCode(String value) {
    ShortCode {                                        // runs before the field is set
        if (value == null || !value.matches("[0-9a-zA-Z]{7}"))
            throw new IllegalArgumentException("a short code is exactly 7 base62 characters");
    }
}

record ShortLink(ShortCode code, String longUrl, Instant createdAt) {
    ShortLink {
        if (code == null || createdAt == null) throw new IllegalArgumentException("code and creation time are required");
        if (longUrl == null || !(longUrl.startsWith("https://") || longUrl.startsWith("http://")))
            throw new IllegalArgumentException("only http and https links can be shortened");
    }
}
```

Now an invalid link simply cannot exist. Any method that receives a `ShortLink` can trust it without checking it again. Wrapping the code in its own `ShortCode` type follows the same idea: a method that receives a `ShortCode` never needs to re-check the 7-character base62 format from Basics 1, and nobody can accidentally pass a long URL where a code was expected.

!!! warning "A common trap"
    Making every field private and then adding a public setter for each one is not encapsulation. Callers can still put the object into any state they like, so the rules still live in the callers. Only add methods that keep the object valid.

!!! question "Practice"
    What is wrong with this class, and how would you fix it?

    ```java
    class Cart {
        public List<Item> items = new ArrayList<>();
        public double total;
    }
    // A caller elsewhere:
    cart.items.add(item);
    cart.total += item.price();
    ```

??? success "Answer"
    The rule "the total always equals the sum of the item prices" lives in the callers. If any caller adds an item and forgets to update the total, the cart becomes wrong, and nothing detects it. The fix is to make the fields private and give the cart an `addItem(Item item)` method that updates both together, or, even simpler, to compute `total()` from the items whenever it is asked for.

### Level 2: Abstraction, hiding the how

**Abstraction** means callers depend on *what* an object does, not *how* it does it. The caller states its intent, and the details stay hidden behind a simple interface.

In `LinkManager`, the redirect method checks Redis, falls back to a SQL query, and then fills the cache, all before it can do its actual job. The code that decides whether a visitor may follow a link should not need to know how links are stored. We hide storage behind an interface:

```java
interface LinkRepository {
    Optional<ShortLink> findByCode(ShortCode code);
    void save(ShortLink link);
}

final class PostgresLinkRepository implements LinkRepository {
    public Optional<ShortLink> findByCode(ShortCode code) {
        // the SQL query, and the mapping from table rows to ShortLink objects, live here and only here
    }
    public void save(ShortLink link) { ... }
}
```

Notice that `findByCode` returns an `Optional` rather than a link that might be `null`. A good abstraction hides details the caller does not need, but it must not hide information the caller needs in order to make a decision. Unknown codes are normal, because people mistype links, and the caller must decide to show a "not found" page. So "nothing was found" is part of the contract. The messy version simply forgot about this case.

What about the cache? It has disappeared from the business logic as well. **Basics 3** shows how to put it back behind this same interface without editing `PostgresLinkRepository` at all.

!!! question "Practice"
    A caller exports a report by opening a file, writing a header row, writing every data row, flushing the stream, and closing the file. What would a better abstraction look like?

??? success "Answer"
    Hide the steps behind an intent-based method such as `reportExporter.export(report, destination)`. The caller only expresses what it wants, and the file-handling steps live inside one exporter class. If the format later changes from CSV to Excel, only the exporter changes, and none of its callers do.

### Level 3: Polymorphism, replacing the type switch

**Polymorphism** means the same method call can behave differently depending on which object receives it. It lets you replace `if` and `switch` statements that check an object's type with a single call through an interface.

In `LinkManager`, every new link feature means editing the `switch`. Worse, in real code the same `switch` on link type tends to appear in several places, such as the redirect, the link preview page, and the admin screen that explains why a link is blocked, and every one of them must be found and updated.

Instead, each link type becomes its own class behind one interface:

```java
enum RedirectDecision { ALLOW, GONE, UNAUTHORIZED, FORBIDDEN }

record Visit(Instant time, String password, String country) {}

interface LinkRule {
    RedirectDecision check(Visit visit);
}

final class ExpiryRule implements LinkRule {
    private final Instant expiresAt;
    ExpiryRule(Instant expiresAt) { this.expiresAt = expiresAt; }

    public RedirectDecision check(Visit visit) {
        return visit.time().isBefore(expiresAt) ? RedirectDecision.ALLOW : RedirectDecision.GONE;
    }
}
// PasswordRule and CountryRule follow exactly the same shape.
```

The `switch` disappears, and one call, `rule.check(visit)`, works for every rule, including rules added later. When marketing asks for links that only work during a campaign, that becomes a new class, and none of the existing, already-tested rules are edited.

!!! tip "A switch is not always wrong"
    Polymorphism is the right tool when new types keep arriving and each type has its own behavior. A plain `switch` is perfectly fine for a small, fixed set of values that rarely changes, such as the days of the week. Choose based on what is likely to change.

??? info "Go deeper (optional): sealed types and exhaustive switches"
    Modern Java offers a middle ground. A `sealed` interface lists every allowed implementation, and a `switch` over it must handle every one of them, or the code does not compile:

    ```java
    sealed interface Shape permits Circle, Square {}
    record Circle(double radius) implements Shape {}
    record Square(double side) implements Shape {}

    double area(Shape shape) {
        return switch (shape) {                        // no default branch is needed
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Square s -> s.side() * s.side();
        };
    }
    ```

    The trade-off is known as the *expression problem*. Polymorphism makes adding a new **type** cheap and a new **operation** expensive; a sealed switch is the reverse, and the compiler points out every switch that a new type must update.

!!! question "Practice"
    How would you remove the type checks from this method?

    ```java
    double area(Shape shape) {
        if (shape.type.equals("circle")) return Math.PI * shape.radius * shape.radius;
        if (shape.type.equals("square")) return shape.side * shape.side;
        throw new IllegalArgumentException("unknown shape");
    }
    ```

??? success "Answer"
    Make `Shape` an interface with an `area()` method, and let `Circle` and `Square` each implement it. The caller then simply calls `shape.area()`. A new shape, such as a triangle, becomes a new class, and the existing code does not change.

### Level 4: Composition over inheritance

**Inheritance** creates an *is-a* relationship: a subclass reuses its parent's code and promises to behave like its parent everywhere. **Composition** creates a *has-a* relationship: an object holds other objects and hands work over to them.

The classic illustration is a bird that can fly, and a penguin that cannot:

![Comparison of inheritance and composition for flight behavior](assets/topic-02/composition_vs_inheritance.png)

If `Penguin extends Bird` and overrides `fly()` to throw an exception, any code that calls `bird.fly()` on a list of birds crashes on the penguin. With composition, a bird *has* a flight behavior, and a penguin is simply a bird given `NoFlight`. No method is overridden, and nothing breaks.

The URL shortener runs into a similar problem as soon as a customer asks for a link that both expires *and* needs a password. The old `type` field can hold only one value. Inheritance tempts us towards `ExpiringLink extends ShortLink` and `PasswordLink extends ShortLink`, and then `ExpiringPasswordLink`, `CountryLockedPasswordLink`, and so on. Three features already allow seven combinations, and every new feature doubles the count. Composition avoids that explosion: a link *has* a list of rules, and it allows a visit only when every rule does.

```java
record ShortLink(ShortCode code, String longUrl, Instant createdAt, List<LinkRule> rules) {
    ShortLink {
        // ...the same checks as in Level 1...
        rules = List.copyOf(rules);                    // a private copy that callers cannot modify later
    }

    RedirectDecision check(Visit visit) {
        for (LinkRule rule : rules) {
            RedirectDecision decision = rule.check(visit);
            if (decision != RedirectDecision.ALLOW) return decision;   // the first rule that says no wins
        }
        return RedirectDecision.ALLOW;
    }
}

// An expiring, password-protected link is simply a link with two rules:
new ShortLink(code, longUrl, now, List.of(new ExpiryRule(nextFriday), new PasswordRule(passwordHash)));
```

A new feature is one new rule class, and it combines with every existing rule for free. `List.copyOf` is encapsulation at work again: without it, a caller could quietly add or remove rules after the link was created.

Inheritance is still the right tool when the relationship is a true *is-a*, the hierarchy is shallow (one or two levels), and every subclass keeps every promise its parent makes. A quick test: if you are about to override a method just to throw an exception or do nothing, the relationship was never *is-a*, so use composition instead.

??? info "Go deeper (optional): the fragile base class problem"
    Inheritance ties a subclass to its parent's *implementation*, not just its interface. This example, from the book *Effective Java*, tries to count how many items are added to a set:

    ```java
    class InstrumentedHashSet<E> extends HashSet<E> {
        int addCount = 0;
        @Override public boolean add(E e) { addCount++; return super.add(e); }
        @Override public boolean addAll(Collection<? extends E> c) { addCount += c.size(); return super.addAll(c); }
    }
    // addAll(List.of("a", "b", "c")) leaves addCount at 6, not 3
    ```

    Internally, `HashSet.addAll` calls `add` once per item, so every item is counted twice. Nothing in the documentation promises or forbids this, so the subclass broke because of a hidden detail inside its parent. Wrapping a `Set` and forwarding calls to it (composition) avoids the problem, because the wrapper no longer depends on how `HashSet` works inside. That wrapping technique is the *Decorator* pattern, covered in **Basics 3 (Creational & Structural Design Patterns)**.

!!! question "Practice"
    Some older Java code declares `class Stack<E> extends ArrayList<E>`. Why is that a poor design?

??? success "Answer"
    A stack should only allow adding and removing items at the top. By extending `ArrayList`, the stack also inherits methods such as `add(index, item)` and `remove(index)`, so any caller can insert or remove items in the middle and break the stack's main rule. A stack is not really a list. It should *have* a private list and expose only `push`, `pop`, and `peek`.

---

## 3. Coupling and cohesion (Level 5)

![Quadrant of coupling against cohesion with the modular quadrant as the goal](assets/topic-02/coupling_cohesion.png)

Coupling and cohesion are the two measurements behind almost every design principle.

- **Cohesion** asks whether the code inside one class belongs together. A class has high cohesion when everything in it serves one purpose and changes for the same reason.
- **Coupling** asks how much one class knows about another. Two classes are tightly coupled when a change in one forces a change in the other.

The goal is the green quadrant: high cohesion and low coupling, so that every change stays local. The original `LinkManager` sits in the red quadrant. It mixes Redis, Postgres, link rules, and click tracking in one class (low cohesion), and it creates those dependencies directly, so it is welded to all of them (high coupling). After Levels 1 to 4, each class has one job, and classes talk to each other only through small interfaces such as `LinkRepository` and `LinkRule`.

A practical habit that reduces coupling is **"tell, don't ask"**: instead of pulling data out of an object to make a decision elsewhere, ask the object that owns the data to make the decision.

```java
// Ask: the caller digs into the link's internals and makes the decision itself
if (link.getExpiryRule().getExpiresAt().isBefore(Instant.now())) { return GONE; }

// Tell: the link owns its rules, and the caller only states what it wants to know
RedirectDecision decision = link.check(visit);
```

A long chain of getters is coupling you can see. If the way rules are stored ever changes, every caller with a chain like that breaks. This guideline is also known as the *Law of Demeter*: talk to the objects you hold directly, not to the objects inside them.

??? info "Go deeper (optional): the kinds of coupling, from worst to best"
    | Kind of coupling | What it looks like |
    |---|---|
    | Content coupling | One class reaches directly into another class's private fields or internal workings. |
    | Global coupling | Classes share mutable global state, which hides dependencies and makes test results depend on the order the tests run in. |
    | Control coupling | A caller passes a flag that tells the method *what to do*, so the caller must understand how the method works inside. |
    | Stamp coupling | A method receives a whole object, such as a `ShortLink`, when it only needs one value from it, such as the code. |
    | Data coupling | A method receives exactly the values it needs and nothing more. This is the goal. |

!!! question "Practice"
    How would you reduce the coupling in this line?

    ```java
    if (order.getCustomer().getAddress().getCountry().equals("IN")) { applyDomesticShipping(order); }
    ```

??? success "Answer"
    Move the question to the object that owns the data, for example `if (order.isDomestic())`. The order (or the customer it holds) decides how to answer, and the caller no longer depends on how customers, addresses, and countries are structured.

---

## 4. SOLID, one letter at a time (Level 6)

![Five SOLID principles framed as questions about change](assets/topic-02/solid_principles.png)

SOLID is a set of five guidelines for keeping change local. Each letter is best remembered as a question you ask about your code, and each one has a typical symptom, or *smell*, that tells you it is being broken. The sections below apply each letter to the URL shortener.

### S: Single Responsibility

**A class should have only one reason to change.** The useful way to apply this is to ask *who* would ask for the class to change.

The original `LinkManager` is changed by four different groups: the product team adds link features, the trust and safety team blocks malicious URLs, the infrastructure team changes how links are stored and cached, and the analytics team changes what is recorded for each click. Their edits collide in one file. The fix gives each group its own classes, and keeps one small class that coordinates them:

```java
final class ExpiryRule implements LinkRule { ... }                               // product team
final class UrlSafetyChecker { boolean isSafe(String longUrl) { ... } }          // trust and safety team
final class PostgresLinkRepository implements LinkRepository { ... }             // infrastructure team
final class ClickRecorder { void record(ShortCode code, Visit visit) { ... } }   // analytics team
final class LinkService { /* coordinates the others, shown in section 6 */ }
```

**Trap:** single responsibility does not mean "one method per class". Methods that protect the same rule belong together. Splitting them across many files scatters one rule, which is the opposite of the goal.

### O: Open/Closed

**A class should be open for extension but closed for modification.** In plain words, a new case should arrive as a new class, without editing code that is already tested.

Levels 3 and 4 already achieved this for link features. When marketing asks for links that only work during a campaign, we write a `CampaignWindowRule` class. `ShortLink`, the other rules, and the service that resolves links are not edited.

**Trap:** only build extension points for changes you have real evidence for. The product team keeps asking for link features, so a rule extension point is justified. Adding extension points for changes nobody has asked for, such as pluggable short-code formats, is guessing, and that breaks YAGNI (Level 7).

### L: Liskov Substitution

**Any implementation must be usable wherever its interface is expected, without surprising the caller.** Matching the method signatures is the easy part. What matters is that every implementation *behaves* the way the contract promises.

Every new link needs a short code, so the service depends on an interface whose contract makes one promise:

```java
interface CodeGenerator {
    ShortCode next();          // contract: never returns a code that has already been used
}
```

`CounterCodeGenerator`, which turns an ever-increasing counter into base62, keeps that promise. Now imagine a `RandomCodeGenerator` that picks 7 random base62 characters and never checks whether the code is already taken. It compiles and passes a quick test. But because of the *birthday paradox*, a repeated code becomes likely after only about two million links, which is roughly three days of traffic at the 20 million links per month estimated in Basics 1. When it happens, `save` overwrites someone else's link, and their visitors land on the wrong page. That generator cannot be safely substituted for a `CodeGenerator`. A correct random generator checks whether the code exists and tries again, which keeps the promise.

The other common symptom is a method that an implementation cannot support. Suppose a team adds `ReadOnlyLinkRepository`, which reads from a read-only copy of the database (a *replica*) and throws `UnsupportedOperationException` from `save`. Any caller that trusts the `LinkRepository` interface would crash. The fix is to model capabilities honestly: give read-only callers a separate `LinkReader` interface that contains only `findByCode`.

The classic interview example is `Square extends Rectangle`. Code that sets a rectangle's width and then its height expects both values to stick, but a square must keep its sides equal, so it silently changes the other side and surprises the caller.

??? info "Go deeper (optional): the four formal substitution rules"
    | Rule | Meaning | Violation example |
    |---|---|---|
    | Preconditions | An implementation cannot demand more from callers than the interface does. | The interface accepts any valid http or https URL, but one implementation rejects URLs longer than 100 characters. |
    | Postconditions | An implementation cannot promise less than the interface does. | The interface promises a code that was never used before, but one generator sometimes returns a duplicate. |
    | Invariants | An implementation must keep every rule the interface keeps true. | A `Square` breaks the rectangle rule that width and height can change independently. |
    | Exceptions | An implementation cannot add new ways to fail. | The interface never throws from `save` for a valid link, but a read-only implementation throws `UnsupportedOperationException`. |

### I: Interface Segregation

**No caller should be forced to depend on methods it does not use.** Interfaces should be shaped around what each kind of caller actually needs.

Suppose `LinkRepository` grew over time to include everything anyone asked for:

```java
// Too big: the redirect path only calls findByCode, but every implementation must provide everything
interface LinkRepository {
    Optional<ShortLink> findByCode(ShortCode code);
    void save(ShortLink link);
    List<ShortLink> topLinks(int limit);                          // only the dashboards need this
    Map<String, Long> clicksByCountry(ShortCode code);            // only the dashboards need this
}

// Better: small interfaces, one per kind of caller
interface LinkRepository { Optional<ShortLink> findByCode(ShortCode code); void save(ShortLink link); }
interface LinkStats      { List<ShortLink> topLinks(int limit); Map<String, Long> clicksByCountry(ShortCode code); }
```

Basics 1 already put click analytics in a separate store from the links themselves, and the interfaces now follow the same split. The redirect path depends only on `findByCode`, so it is not affected when the analytics team changes its reports, and the in-memory fake used in tests no longer has to pretend to produce statistics.

**Trap:** split interfaces by what callers need, not mechanically by method. A codebase where every interface has exactly one method is just as hard to work with as one giant interface.

### D: Dependency Inversion

**Business logic should depend on interfaces it owns, not on concrete infrastructure.** Infrastructure, such as databases and third-party services, then plugs in behind those interfaces.

The original `LinkManager` creates `new PostgresClient(DB_URL)` itself. That welds the business logic to Postgres, makes it impossible to test without a real database, and means switching databases requires editing the business logic. The fix is to depend on the `LinkRepository` interface and receive the implementation from outside, through the constructor:

```java
final class LinkService {
    private final LinkRepository links;

    LinkService(LinkRepository links) {        // handed in, never created here
        this.links = links;
    }
}
// In production, the wiring passes a PostgresLinkRepository. In tests, it passes an InMemoryLinkRepository.
```

The diagram shows the change. Before, the business logic points at Postgres. After, both the real Postgres repository and the in-memory test fake point up at an interface that belongs to the business logic.

![Dependency inversion: before, the link service depends on Postgres; after, both repositories depend on a policy-owned interface](assets/topic-02/dependency_inversion.png)

**Trap:** the interface must be shaped by what the business logic needs, such as `findByCode(code)`, not copied from the database driver's API, such as `executeQuery(sql, parameters)`. An interface that mirrors one vendor adds a layer without removing the dependency. Also note that *dependency injection* (passing dependencies in through the constructor) is just the technique used to wire this design; the principle is about which way the dependency points.

!!! question "Practice: which SOLID letter does each snippet break?"
    1. `class InvoiceService { Money calculate(...); void saveToDatabase(...); void emailPdf(...); }`
    2. A `discount(Customer c)` method with an `if / else if` branch for every customer tier, and marketing adds a new tier every quarter.
    3. `class ReadOnlyFile extends File { @Override void write(byte[] data) { throw new UnsupportedOperationException(); } }`
    4. `interface Printer { void print(); void scan(); void fax(); }`, where the `BasicPrinter` implementation throws on `scan` and `fax`.
    5. `class ReportService { private final PostgresClient db = new PostgresClient("prod-db-host"); }`

??? success "Answer"
    1. **S (Single Responsibility).** Calculation, storage, and email change for different reasons and are requested by different people, so they belong in different classes.
    2. **O (Open/Closed).** Every new tier edits tested code. Each tier could instead be its own discount rule class.
    3. **L (Liskov Substitution).** Code that writes to a `File` crashes when it receives a `ReadOnlyFile`, so the subtype cannot be safely substituted.
    4. **I (Interface Segregation),** and also L. The basic printer is forced to provide methods it cannot support. Splitting the interface into `Printer`, `Scanner`, and `Fax` fixes both problems.
    5. **D (Dependency Inversion).** The service creates its own database client, so it cannot be tested without a real database, and switching databases means editing the service.

---

## 5. DRY, KISS, and YAGNI (Level 7)

![DRY, KISS, and YAGNI pulling from opposite ends of the abstraction spectrum](assets/topic-02/clean_code_guardrails.png)

SOLID tells you *where* responsibilities should go. These three guidelines tell you *how much* abstraction to build. They pull in opposite directions, and good design sits in the middle.

### DRY: Don't Repeat Yourself

**Every piece of knowledge should have one owner.** If the same business rule is written in several places, the copies eventually drift apart.

Suppose the base62 alphabet, `0-9`, `a-z`, `A-Z` in that order, is typed out in three places: the `ShortCode` format check, the counter generator that turns numbers into codes, and an admin tool that turns codes back into numbers. If someone reorders the characters in one copy, codes no longer decode to the numbers that created them, and nothing fails loudly. A single `Base62` class that owns the alphabet and both directions of conversion gives that knowledge one home.

**Trap:** DRY is about duplicated *knowledge*, not duplicated *text*. Two methods that look identical but belong to different owners, such as signup validation and identity verification, should stay separate. If you merge them, the first requirement that applies to only one of them adds a boolean flag, and then another. As Sandi Metz put it, "duplication is far cheaper than the wrong abstraction". A useful tie-breaker is the **rule of three**: tolerate a second copy, and extract a shared abstraction when a third copy appears.

### KISS: Keep It Simple

**Every layer of complexity must buy a capability you actually need.** With three link rules, it can be tempting to build a plugin framework that discovers rule classes automatically and sorts them by priority. The plain list of rules from Level 4 already does the job, and anyone can read it in seconds.

**Trap:** KISS removes complexity that the design added by accident. It does not mean ignoring complexity that is genuinely part of the problem, such as time zones in expiry dates or collisions in random codes. Flattening real rules into something that looks simple but handles edge cases wrongly is a bug.

### YAGNI: You Aren't Gonna Need It

**Do not build for a future that nobody has asked for.** The `LinkRepository` interface is worth having today: it costs one small file, and it lets us test with an in-memory store. Building custom-domain support or QR-code generation "just in case" is not worth it. Basics 1 explicitly put custom domains out of scope, and code written against guessed requirements is usually wrong by the time the real need arrives. Keep the extension points that are cheap and proven, but do not build the extensions early.

!!! question "Practice"
    The signup flow and the identity-verification flow each contain an identical 10-line method that validates a user's name and date of birth. A teammate wants to merge them into one shared method. What should you consider?

??? success "Answer"
    Ask whether the two methods share the same *knowledge* or only look the same today. The two flows are owned by different teams and follow different rules: identity verification is usually driven by legal requirements, while signup is driven by product decisions. They are likely to diverge, so keeping them separate is often the better choice. If the rule really is shared, for example a single company-wide definition of a valid date of birth, then extract that one rule into its own class and let both flows use it.

---

## 6. Putting it together: the URL shortener's classes

After all seven levels, the messy `LinkManager` has become a set of small classes, each with one clear job:

![URL shortener class diagram with policy above and replaceable implementations below a boundary](assets/topic-02/link_service_architecture.png)

The dashed line in the diagram separates stable business logic (above) from details that change more often (below). The classes above the line never mention Postgres, Redis, or a particular code scheme, so the store can be replaced, and a new code scheme added, without editing them.

| Class | What it is responsible for | Who asks for it to change |
|---|---|---|
| `ShortCode` | It holds one valid 7-character base62 code. | Rarely anyone, unless the code format changes. |
| `ShortLink` | It holds one valid link with its rules, and decides whether a visit may follow it. | Rarely anyone, because new link features arrive as new rules. |
| `LinkRule` and its rules (`ExpiryRule`, `PasswordRule`, `CountryRule`) | Each rule decides one thing about a visit. | The product team, when link features are added or changed. |
| `CodeGenerator` and `CounterCodeGenerator` | It produces a code that has never been used before. | The engineering team, when the code scheme changes. |
| `LinkRepository` and `PostgresLinkRepository` | It stores links and finds them by code. | The infrastructure team, when storage changes. |
| `UrlSafetyChecker` | It rejects URLs that are known to be malicious. | The trust and safety team. |
| `ClickRecorder` | It publishes a click event to the queue from Basics 1. | The analytics team. |
| `LinkService` | It coordinates the others for the two main flows: shortening a URL and resolving a code. | Anyone who changes one of those overall workflows. |

The coordinating class is now short, and it contains no storage, code-scheme, or link-rule details of its own:

```java
final class LinkService {
    private final CodeGenerator codes;
    private final LinkRepository links;
    private final UrlSafetyChecker safety;
    private final ClickRecorder clicks;
    // The constructor receives all four dependencies, exactly as in the Dependency Inversion section.

    ShortCode shorten(String longUrl, List<LinkRule> rules) {
        if (!safety.isSafe(longUrl)) throw new UnsafeUrlException(longUrl);
        ShortLink link = new ShortLink(codes.next(), longUrl, Instant.now(), rules);
        links.save(link);
        return link.code();
    }

    RedirectResult resolve(ShortCode code, Visit visit) {       // the web layer turns this into an HTTP response
        Optional<ShortLink> found = links.findByCode(code);
        if (found.isEmpty()) return RedirectResult.notFound();
        RedirectDecision decision = found.get().check(visit);
        if (decision == RedirectDecision.ALLOW) clicks.record(code, visit);
        return RedirectResult.of(decision, found.get().longUrl());
    }
}
```

The real test of a design is how it handles change. Here is what each likely change request touches:

| Change request | What you edit | What you add | What stays untouched |
|---|---|---|---|
| Add links that only work during a campaign. | You edit only the API code that creates links with the new rule. | You add a `CampaignWindowRule` class. | `ShortLink`, `LinkService`, and every other rule stay untouched. |
| Put a cache in front of the database. | You edit only the wiring. | You add a caching repository class, as shown in Basics 3. | `LinkService` and `PostgresLinkRepository` stay untouched. |
| Switch from counter-based codes to random codes. | You edit only the wiring. | You add a `RandomCodeGenerator` that checks for collisions. | Every other class stays untouched. |
| Block a newly discovered kind of malicious URL. | You edit `UrlSafetyChecker`. | You add tests for the new case. | Every other class stays untouched. |
| Let owners change where an existing link points. | You edit `LinkService` and `ShortLink`, because the workflow itself changes. | You add an "update link" flow to the API. | The rules, the code generators, and the repository contract stay untouched. |

The last row is important. Editing links changes a *workflow*, and the coordinating class is supposed to change for workflow reasons. No design absorbs every possible change, and saying so honestly is a stronger answer than claiming the design is open to anything.

??? info "Go deeper (optional): proving substitution with contract tests"
    Level 6 said every implementation must keep its interface's promises. A *contract test* turns those promises into something the build checks. You write the tests once, against the interface, and every implementation's test class inherits them:

    ```java
    abstract class LinkRepositoryContractTest {
        protected abstract LinkRepository repository();       // each implementation's test supplies one

        @Test void unknownCodeIsEmpty() {
            assertTrue(repository().findByCode(new ShortCode("zzzzzzz")).isEmpty());
        }
        @Test void savedLinkCanBeFound() {
            LinkRepository repository = repository();
            repository.save(sampleLink());
            assertEquals(Optional.of(sampleLink()), repository.findByCode(sampleLink().code()));
        }
    }
    class InMemoryLinkRepositoryTest extends LinkRepositoryContractTest { ... }
    class PostgresLinkRepositoryTest extends LinkRepositoryContractTest { ... }   // runs against a real test database
    ```

    This matters most for fakes. If the in-memory fake behaves differently from Postgres, every test that uses it proves the wrong thing. Running the same suite against both keeps the fake honest. Inheritance is the right tool here, because every concrete test class truly *is* a repository contract test.

---

## 7. Design smells to recognize

![Design smells connected to expensive change](assets/topic-02/design_smells.png)

A *smell* is a visible symptom that a design will make change expensive. Learning to spot these is the fastest way to apply the principles in real code reviews. Each smell below maps to one of the principles on this page.

| Smell | How you notice it | Principle at stake | Usual fix |
|---|---|---|---|
| **God class** | One class is edited in most pull requests, often with a name ending in `Manager`. | Single Responsibility | Split it into one class per group of people that asks for changes. |
| **Type switch** | The same `switch` or `instanceof` check on a type appears in several places. | Open/Closed | Replace the checks with an interface and one implementation per type. |
| **Refused bequest** | A subclass overrides inherited methods just to throw an exception or do nothing. | Liskov Substitution | Stop inheriting, and compose the capabilities that the class really has. |
| **Fat interface** | Implementations are forced to write empty or throwing versions of methods they cannot support. | Interface Segregation | Split the interface into smaller ones shaped around each kind of caller. |
| **Concrete coupling** | Business logic creates databases or provider clients itself with `new`. | Dependency Inversion | Depend on an interface owned by the business logic, and pass the implementation in. |
| **Shotgun surgery** | Changing one business rule means editing many files. | DRY | Move that knowledge into one owner that every other class uses. |

!!! warning "Refactor because of evidence, not taste"
    "This could be cleaner" is not a strong reason to restructure code. "This rule changed three times, and we missed one copy twice" is. Name the change that hurts, and make the smallest structural change that keeps it local.

---

## 8. Test yourself

These three problems increase in difficulty. Try each one on paper before opening the answer.

!!! question "Problem 1 (warm-up): a user profile"
    ```java
    class User {
        public String email;
        private int age;
        public void setAge(int age) { this.age = age; }
    }
    ```
    Which principle does this break, and how would you fix it?

??? success "Answer"
    It breaks **encapsulation**. The `email` field is public, so anyone can set it to an invalid value, and `setAge` accepts negative ages. Make the fields private and final, validate both values once in the constructor (or in an `Email` type that validates itself), and only allow changes through methods that enforce the rules, such as `changeEmail(Email newEmail)`.

!!! question "Problem 2 (code review): a report generator"
    ```java
    class ReportGenerator extends PostgresConnection {
        String generate(String format) {
            if (format.equals("PDF")) { /* build a PDF from query results */ }
            else if (format.equals("CSV")) { /* build a CSV from query results */ }
            ...
        }
    }
    ```
    This class has three separate problems. Name each one, the principle it breaks, and the fix.

??? success "Answer"
    1. **Inheriting to reuse code.** A report generator is not a database connection; it only *uses* one. Extending `PostgresConnection` exposes every connection method on the generator. Use composition: the generator should *have* a data source.
    2. **A type switch on the format** breaks Open/Closed, because every new format edits this method. Give each format its own class behind a `ReportFormatter` interface.
    3. **Concrete coupling to Postgres** breaks Dependency Inversion, because the generator cannot be tested without a real database. Depend on a small `ReportData` interface shaped around what the report needs, and pass the Postgres implementation in from outside.

!!! question "Problem 3 (design): a logging library"
    Design the main classes for a logging library. Logs can be written to the console, a file, or a remote server, and each log line can be formatted as plain text or JSON. New destinations and formats are expected in the future.

??? success "Answer"
    The tempting inheritance design creates a class for every combination, such as `ConsoleJsonLogger` and `FilePlainLogger`. Three destinations and two formats already need six classes, and every new format adds three more.

    Composition keeps the two kinds of variation independent:

    ```java
    interface Formatter   { String format(LogEvent event); }          // PlainFormatter, JsonFormatter
    interface Destination { void write(String line); }                // ConsoleDestination, FileDestination, RemoteDestination

    final class Logger {
        private final Formatter formatter;
        private final List<Destination> destinations;
        // The constructor receives the formatter and the destinations from outside.

        void log(LogEvent event) {
            String line = formatter.format(event);
            for (Destination destination : destinations) destination.write(line);
        }
    }
    ```

    A new format is one new `Formatter` class, and a new destination is one new `Destination` class, with no combinations to multiply. Each class has a single responsibility, the `Logger` depends only on interfaces (Dependency Inversion), and tests can pass in a fake destination that simply records lines.

---

## 9. How this shows up in an LLD interview

![Six-stage low-level design interview framework](assets/topic-02/lld_interview_framework.png)

A low-level design (LLD) interview asks you to design the classes for a small system, and often to write the core code. It follows the same funnel as the system design interview in Basics 1, one level closer to the code.

| Stage | What you are trying to achieve |
|---|---|
| Clarify | Agree on the main use cases, say what is out of scope, and name one or two changes that are likely to come. |
| Model | List the main classes, and give each one a single-sentence responsibility. |
| Contract | Define the key interfaces and the rules each object guarantees. |
| Relate | Draw a class diagram that shows which classes have, implement, or depend on which others. |
| Code | Write the main flow in real code, including at least one failure case. |
| Extend | Walk through a likely change and show that it becomes a new class rather than an edit to existing code. |

!!! tip "The LLD round in one sentence"
    Find the changes that are likely to come, give each one a single owner behind a small interface, and show that a new requirement becomes a new class rather than an edit.

### Checklist

```text
[ ] Keep each object's data private, and enforce its rules in one place.
[ ] Let callers depend on what an object does, not on how it does it.
[ ] Replace repeated type switches with an interface and one class per type.
[ ] Use composition for capabilities; use inheritance only for a true, stable is-a.
[ ] Aim for high cohesion inside classes and low coupling between them.
[ ] Check each SOLID question: who changes it, can it extend, can it substitute,
    does each caller use the whole interface, and can it run without real infrastructure?
[ ] Apply DRY to knowledge, KISS to mechanisms, and YAGNI to guesses about the future.
[ ] Show how a likely change becomes a new class, and admit which changes the design does not absorb.
```

### What comes next

| Topic you may have heard about | Where it is covered |
|---|---|
| Factory, Builder, Singleton, Adapter, Decorator, and other structural patterns, applied to these same URL shortener classes | Basics 3: Creational & Structural Design Patterns |
| Strategy (the pattern behind `LinkRule` and `CodeGenerator`), Observer, Template Method, and other behavioral patterns | Advanced 1: Behavioral Design Patterns |
| Full machine-coding case studies, such as a parking lot or a ticket booking system | Advanced 2: Real-World Machine Coding Case Studies |
| Service boundaries, modular monoliths, and microservices | Basics 5: Architecture Styles & Service Decomposition |
| Cache strategies, expiry, and eviction | Basics 9: Caching Core |
| Queues that process click events in the background | Basics 13: Asynchronous Processing Basics |
| Generating unique short codes across many servers at once | Basics 15: Distributed ID Generation |
