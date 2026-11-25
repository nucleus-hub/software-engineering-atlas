# LLD: Creational & Structural Design Patterns

> A visual guide to the patterns that decide **who builds an object** and **how objects are wired together**. Use it to choose the smallest pattern that contains a change you expect, tell look-alike patterns apart, and defend every pattern you put on the whiteboard.

---

## 1. Start from the change, not the pattern

A design pattern is a well-known, named solution to a common design problem. This page covers two families: **creational** patterns decide *who builds an object*, and **structural** patterns decide *how objects are wired together*. Sections 3 and 4 explain each pattern, and section 6 compares them side by side.

The usual beginner mistake is to start from a pattern ("let's add a Factory here"). Start from the change you expect instead, and only then pick a pattern:

![Three questions before adding a pattern, answered with the payment gateway example](assets/topic-03/pattern_selection.png)

In the example, a second payment provider is really coming, so an Adapter is worth the extra class. If you cannot name a change like that, plain code is the right answer, and you do not need a pattern yet.

---

## 2. Three ideas before the patterns

### Every pattern has a cost

A pattern makes one kind of change easy. In return, it adds extra classes, and an extra step that everyone reading the code has to follow. So use a pattern only when the change it helps with is actually expected: the YAGNI rule from [Basics 2](02_LLD_Object_Oriented_Principles_And_Clean_Code.md).

Patterns are also shared vocabulary. Once two engineers know the names, "wrap the Stripe adapter in a retry decorator" describes a whole design in one sentence. That is a big part of their value in an interview.

### Two families of patterns

![Creational patterns create objects; structural patterns connect them](assets/topic-03/patterns_mental_model.png)

- **Creational patterns** answer: *who creates this object, and how?*
- **Structural patterns** answer: *how do these objects fit together?*

Here is the problem both families solve, in one class:

```java
final class Checkout {
    ChargeResult pay(Order order) {
        StripeGateway gateway = new StripeGateway(apiKey);   // Checkout creates Stripe itself...
        return gateway.charge(order.total());                 // ...and calls Stripe's own API
    }
}
```

`Checkout` has to know which payment provider to use, how to create it, and how its API works. Switching provider, or testing without making real payments, means editing `Checkout`. A creational pattern moves the `new StripeGateway(...)` somewhere else. A structural pattern, such as Adapter, puts your own interface in front of Stripe's, so `Checkout` never sees Stripe's API.

### Where objects should be created

In the example above, the problem is the line `new StripeGateway(apiKey)` *inside* `Checkout`. The fix: `Checkout` stops creating the gateway itself, and receives it through its constructor instead.

```java
final class Checkout {
    private final PaymentGateway gateway;          // an interface, not Stripe

    Checkout(PaymentGateway gateway) {             // someone else creates it and hands it in
        this.gateway = gateway;
    }
    ChargeResult pay(Order order) {
        return gateway.charge(order.total());
    }
}
```

Now `Checkout` works with any payment provider that implements `PaymentGateway`, and a test can hand it a fake one.

But *someone* still has to call `new`. That job moves to one place that runs when the application starts, usually `main()`. It creates the real objects, connects them, and starts the app. This place is called the **composition root**:

```java
public static void main(String[] args) {
    PaymentGateway gateway = new StripeGateway(config.stripeKey());   // 1. create the real object
    Checkout checkout = new Checkout(gateway);                        // 2. hand it to the class that needs it
    server.start(checkout);                                           // 3. start the app
}
```

#### The same thing in Spring

In a Spring Boot application, you do not write that `main()` wiring yourself. You mark your classes with annotations, and Spring becomes the composition root:

```java
@Component
class StripeGateway implements PaymentGateway {
    StripeGateway(@Value("${stripe.api-key}") String apiKey) { ... }   // Spring reads the key from config
}

@Service
class Checkout {
    private final PaymentGateway gateway;
    Checkout(PaymentGateway gateway) { this.gateway = gateway; }      // Spring passes in a StripeGateway
}

@SpringBootApplication
public class ShopApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);          // creates and connects everything
    }
}
```

When the application starts, Spring:

1. Finds every class marked `@Component` or `@Service`.
2. Reads each constructor to see what it needs: `Checkout` needs a `PaymentGateway`, and `StripeGateway` is one.
3. Creates `StripeGateway` first, then creates `Checkout` and passes the gateway in.

`Checkout` is the same plain class in both versions. It never knows who created its gateway, which is the whole point. By default, Spring creates just one object of each class and shares it: one instance, without the global access that makes the Singleton pattern risky.

#### When you still need a creational pattern

The composition root runs once, at start-up. That is enough for most objects. It cannot help when an object depends on something that happens *later*, such as the payment method a customer picks at checkout, or when a *new* object is needed every time, such as a `Pizza` for every order. Those are the cases the creational patterns below are for.

---

## 3. Creational patterns

![Five creational patterns: what each does and when to use it](assets/topic-03/creational_patterns.png)

Creational patterns are about creating objects. Each one below starts with what it does in plain words, then an example, then what it costs. (Pattern books call the object being created the *product*; this page just says "the object".)

### Start simple: constructors and static factory methods

Most objects need no pattern at all. A **constructor** is fine when there are two or three required values and their meaning is obvious.

A **static factory method** is a static method that creates the object for you. Its big advantage is a *name*. Take a temperature: `new Temperature(25)` cannot say whether 25 is Celsius or Fahrenheit, and Java does not allow two constructors that both take one `double`. Two named methods solve it:

```java
final class Temperature {
    private final double degreesCelsius;

    private Temperature(double degreesCelsius) {   // private: callers must use the methods below
        this.degreesCelsius = degreesCelsius;
    }
    static Temperature celsius(double value)    { return new Temperature(value); }
    static Temperature fahrenheit(double value) { return new Temperature((value - 32) * 5 / 9); }
}

Temperature today = Temperature.celsius(25);       // the call says exactly what it means
Temperature oven  = Temperature.fahrenheit(350);
```

You already use static factory methods every day: `List.of(1, 2, 3)`, `LocalDate.of(2025, 1, 31)`, and `Integer.valueOf(42)`, which hands back an existing cached object for small numbers instead of creating a new one.

A **simple factory** goes one step further: one method that picks which class to create from its input, such as `SenderFactory.forChannel(EMAIL)` returning an `EmailSender`. It is very common, but it is *not* the Factory Method pattern below, and interviewers like to check that you know the difference.

### Factory Method: subclasses decide what to create

**What it is:** a parent class defines the steps of a process, and leaves one step, "create the object I need", to its subclasses.

A delivery company runs every delivery the same way: load the order, then travel to the address. Only the vehicle differs:

```java
abstract class Delivery {
    abstract Vehicle createVehicle();             // the factory method: each subclass decides

    void deliver(Order order) {                   // the same steps for every delivery
        Vehicle vehicle = createVehicle();
        vehicle.load(order);
        vehicle.travelTo(order.address());
    }
}
final class RoadDelivery extends Delivery { Vehicle createVehicle() { return new Truck(); } }
final class SeaDelivery  extends Delivery { Vehicle createVehicle() { return new Ship(); } }
```

Adding air delivery means one new `AirDelivery` subclass. The `deliver()` steps are never edited.

**Watch out:** every new variant needs a new subclass. If you only need to pick a class from a value, a simple factory is simpler.

### Abstract Factory: create a matching set of objects

**What it is:** a *factory* is an object whose only job is to create other objects. An Abstract Factory creates a whole **set of objects that belong together**, with one factory per set. You pick one factory, and everything you get from it matches.

Think of a furniture store. Choose the "Modern" collection, and the chair, sofa, and table you get all match; you never end up with a modern chair beside a vintage sofa. In code, each collection is a factory.

An app with light and dark themes works the same way. Its buttons and checkboxes must match, because a dark button next to a light checkbox would be a bug:

```java
interface ThemeFactory {
    Button createButton();
    Checkbox createCheckbox();
}
final class DarkTheme implements ThemeFactory {
    public Button createButton()     { return new DarkButton(); }
    public Checkbox createCheckbox() { return new DarkCheckbox(); }
}
// LightTheme does the same with LightButton and LightCheckbox.
```

The screen is given one factory and asks it for every widget. It never names a theme itself, so it cannot mix them:

```java
void drawSettingsScreen(ThemeFactory theme) {
    Button save = theme.createButton();           // dark if the theme is dark...
    Checkbox alerts = theme.createCheckbox();     // ...and so is this, always
}

drawSettingsScreen(new DarkTheme());              // switch every widget by changing one line
```

**Watch out:** adding a new kind of widget, such as a `Slider`, means editing *every* theme factory. Use it only when mixing would really be a bug.

### Builder: build a complex object step by step

**What it is:** a helper object that collects an object's settings one at a time, using named methods, and creates the finished object when you call `build()`.

**The problem.** When a class has many optional settings, its constructor turns into a row of values that nobody can read:

```java
new Pizza(LARGE, true, STUFFED, false);   // what do true and false mean?
```

**The fix.** With a builder, every value has a name, and you only set what you need:

```java
Pizza pizza = Pizza.builder(LARGE)        // size is required, so it comes first
        .extraCheese()
        .crust(STUFFED)
        .build();                         // checks the order, then creates the pizza
```

![Without a builder, a pile of constructors; with a builder, named steps](assets/topic-03/builder_vs_telescoping.png)

**How it works.** The builder is a small class inside `Pizza`. Each method stores one setting and returns the builder, which is what lets the calls chain. Settings you never call keep their defaults. `build()` checks the rules, and only then creates the `Pizza`:

```java
class Pizza {
    static class Builder {
        private final Size size;
        private boolean extraCheese = false;      // defaults, used if you don't choose
        private boolean mushrooms = false;
        private Crust crust = Crust.CLASSIC;

        Builder(Size size)         { this.size = size; }
        Builder extraCheese()      { this.extraCheese = true; return this; }
        Builder mushrooms()        { this.mushrooms = true; return this; }
        Builder crust(Crust crust) { this.crust = crust; return this; }

        Pizza build() {
            if (crust == Crust.STUFFED && size != Size.LARGE)
                throw new IllegalStateException("stuffed crust is only for large pizzas");
            return new Pizza(size, extraCheese, crust, mushrooms);
        }
    }

    static Builder builder(Size size) { return new Builder(size); }

    private Pizza(Size size, boolean extraCheese, Crust crust, boolean mushrooms) { ... }   // private: only build() calls it
}
```

Because the constructor is private, `build()` is the only way to get a `Pizza`, so an invalid pizza can never be created. In real projects, Lombok's `@Builder` annotation can generate this whole class for you, and Java's `HttpRequest.newBuilder()` works the same way.

**Watch out:** a builder is extra code. For two or three required values, a plain constructor or a record is clearer.

### Prototype: copy an existing object

**What it is:** with Prototype, you create a new object by copying an existing object that is already set up, and then you change only the parts that are different.

**When it helps.** Imagine an email tool where the marketing team keeps a ready-made campaign template. The template already has a subject line and a list of recipients. When the team starts a new campaign, it is easier to copy the template and adjust the copy than to set everything up again from nothing:

```java
EmailTemplate summerSale = template.copy();              // start from the ready-made template
summerSale.addRecipient("new.customer@example.com");     // change only what is different
```

**How to copy correctly.** The copy must get its *own* recipient list. If the copy and the template share one list, changing one of them changes both:

```java
final class EmailTemplate {
    private final String subject;
    private final List<String> recipients;

    EmailTemplate(String subject, List<String> recipients) {
        this.subject = subject;
        this.recipients = recipients;
    }

    void addRecipient(String email) {
        recipients.add(email);
    }

    EmailTemplate copy() {
        return new EmailTemplate(subject, new ArrayList<>(recipients));   // the copy gets its own new list
    }
}
```

The subject does not need copying, because a Java `String` can never be changed once it is created.

**Watch out:** the most common mistake is writing `new EmailTemplate(subject, recipients)` inside `copy()`. That hands the copy the *same* list object as the template, so adding a recipient to the summer sale campaign would silently add them to the original template as well. This mistake is called a **shallow copy**. To avoid it, give the copy its own new version of anything that can change, as `copy()` does above. In Java, write your own `copy()` method like this one instead of using the built-in `Cloneable` interface, which is awkward and easy to get wrong.

### Singleton: only one instance

**What it is:** a Singleton is a class that allows only one object of itself to exist, and that lets any part of the program reach that one object directly.

**When it seems useful.** Some things should exist only once in an application, such as its configuration settings. A Singleton guarantees there is just one, and lets any class get to it without anyone handing it over:

```java
enum AppConfig {                        // Java creates exactly one INSTANCE, and never another
    INSTANCE;

    private final Map<String, String> values = loadFromFile();

    String get(String key) {
        return values.get(key);
    }
}

String databaseUrl = AppConfig.INSTANCE.get("db.url");   // any class, anywhere, can do this
```

**Why it causes problems.** The danger is the "reach it from anywhere" part:

- **Hidden dependencies.** When `OrderService` calls `AppConfig.INSTANCE` inside one of its methods, nothing in its constructor shows that it needs the configuration. You only find out by reading every line of the class.
- **Hard to test.** A test cannot give `OrderService` a fake configuration, because `OrderService` always grabs the real one itself.
- **Shared changes.** If the single object holds data that can change, many threads changing it at the same time can cause bugs that are very hard to find.

**The better option.** Most of the time, you only need *one object*; you do not need *global access* to it. So create the object once at start-up, and pass it to the classes that need it, exactly like the composition root earlier on this page:

```java
Config config = Config.loadFrom(Path.of("app.yaml"));   // created once, at start-up
OrderService orders = new OrderService(config);         // the dependency is visible in the constructor
```

Now the dependency is visible, and a test can simply pass in a fake `Config`. Spring works this way by default: it creates one object of each class and passes it to whoever needs it, so you get a single instance without global access.

**Watch out:** Singleton is the most overused design pattern. Use it only when a second instance would be a real bug *and* passing the object in is not possible. If you do need one, an `enum` like `AppConfig` above is the simplest thread-safe way to write it in Java.

---

## 4. Structural patterns

![Adapter, Decorator, Facade, and Proxy, each shown between your code and the real object](assets/topic-03/wrapper_family.png)

Structural patterns are about how objects fit together. The four main ones all work the same way: they put one object *between* your code and the real object it uses. What makes them different is *why* the object in the middle is there, so in an interview, always give the reason, not just the name.

### Adapter: make a class fit the interface your code expects

**What it is:** an adapter sits between your code and a class whose methods do not match what your code expects, and translates every call from one to the other. It works like a travel plug adapter: neither the plug nor the socket changes, and the adapter makes them fit.

**When it helps.** Checkout expects a `PaymentGateway` with a `charge(request)` method. Stripe's SDK has its own classes, its own method names, and its own errors, and you cannot change Stripe's code. So you write an adapter that implements your interface by calling Stripe:

```java
class StripeAdapter implements PaymentGateway {         // your interface on the outside...
    private final StripeClient stripe;                  // ...Stripe's SDK on the inside

    StripeAdapter(StripeClient stripe) {
        this.stripe = stripe;
    }

    public ChargeResult charge(ChargeRequest request) {
        try {
            StripeCharge charge = stripe.createCharge(request.amountInCents(), request.currency());
            return ChargeResult.approved(charge.id());          // translate Stripe's answer into yours
        } catch (StripeCardException e) {
            return ChargeResult.declined(e.getMessage());       // translate Stripe's errors too
        }
    }
}
```

The rest of your code only ever sees `PaymentGateway`. If Stripe changes its SDK, or you add another provider, only the adapter changes.

**Watch out:** translate errors as carefully as successful results. If the adapter reported a declined card as a success, every class above it would trust the wrong answer.

### Decorator: add a feature without changing the class

**What it is:** a decorator is a class that wraps another object and adds one extra feature to it, without changing that object's methods. Anything that uses the wrapped object cannot tell the difference, except that it now also gets the extra feature. Think of a phone case: the phone still works exactly as before, you still use the same buttons and screen, and the case just adds protection around it.

**When it helps.** `StripeAdapter` charges a card through one method, `charge(request)`. Now payments should be retried when Stripe times out. One option is to add a retry loop straight inside `StripeAdapter`. But then that one class has two jobs: talking to Stripe, and deciding when to retry. A decorator keeps the two apart. You write a new class, `RetryingGateway`, with the very same `charge(request)` method. Inside, it calls the real gateway and only adds the retrying around that call:

```java
class RetryingGateway implements PaymentGateway {     // the same interface as the object it wraps
    private final PaymentGateway inner;               // the gateway being wrapped

    RetryingGateway(PaymentGateway inner) {
        this.inner = inner;
    }

    public ChargeResult charge(ChargeRequest request) {
        for (int attempt = 1; attempt <= 3; attempt++) {
            ChargeResult result = inner.charge(request);     // try the real gateway
            if (!result.isTimeout()) {
                return result;                                // approved, or declined for a real reason: stop here
            }
        }
        return ChargeResult.declined("gateway timed out 3 times");   // out of attempts
    }
}
```

Each attempt calls the wrapped gateway. If it times out, the loop tries again; anything else (approved, or declined for a real reason) is returned straight away.

Because every decorator has the same interface as the object it wraps, you can stack them, each one adding a single feature:

```java
PaymentGateway gateway = new StripeAdapter(stripeClient);    // talks to Stripe
gateway = new AuditingGateway(gateway, auditLog);            // + records every attempt
gateway = new RetryingGateway(gateway);                      // + retries temporary failures
```

Checkout receives `gateway` and has no idea how many layers it has. Each feature lives in its own small class, and adding or removing one is a one-line change.

![The same decorators wrapped in two orders produce different audit trails](assets/topic-03/decorator_ordering.png)

**Watch out:** the order of the layers changes the behavior. In the stack above, audit sits *inside* retry, so every attempt is recorded: three attempts produce three audit entries. Swap the two lines, and audit sees only the final result. Neither order is wrong, but choose it on purpose and be ready to explain why.

### Facade: one simple entry point to many classes

**What it is:** a facade is one class with a simple method that calls several other classes in the right order, so that callers do not have to. It is like a waiter in a restaurant: you place one order, and the waiter deals with the kitchen, the bar, and the bill.

**When it helps.** Paying for an order takes four steps: a fraud check, the tax calculation, the charge itself, and a record in the ledger. Without a facade, every caller would need to know all of those classes and call them in the right order. With a facade, checkout makes a single call, `paymentService.pay(order)`:

```java
class PaymentService {                                         // the facade
    Receipt pay(Order order) {
        fraudCheck.verify(order);                              // 1. stop suspicious orders
        Money total = taxCalculator.totalWithTax(order);       // 2. work out the total
        ChargeRequest request = ChargeRequest.builder().order(order).amount(total).build();
        ChargeResult result = gateways.forCountry(order.country()).charge(request);   // 3. charge the customer
        return ledger.record(order, result);                   // 4. record the result
    }
}
```

**Watch out:** a facade should only *coordinate* the steps; it should not contain business rules. Tax rules belong in the tax calculator, not in `PaymentService`. A facade that keeps collecting rules slowly turns into one huge class that does everything.

### Proxy: control access to the real object

**What it is:** a proxy is a class that stands in for another object, offering the exact same methods, and controls when that real object gets used. Anything calling the proxy cannot tell it apart from the real object, except that the real work may happen later, or not at all. Think of a stunt double on a film set: the double looks like the real actor and stands in for them, and the real actor only appears for the scenes that truly need them.

**When it helps.** A product page shows 100 high-resolution images, but most customers only ever scroll past the first few. One option is to load all 100 images from disk the moment the page opens, but that wastes time loading images nobody looks at. A proxy fixes this: it looks exactly like a real image to the page, but only loads the actual file the first time it is shown:

```java
class LazyImage implements Image {                 // the proxy: same interface as the real image
    private final String fileName;
    private Image real;                            // not loaded yet

    LazyImage(String fileName) {
        this.fileName = fileName;
    }

    public void show() {
        if (real == null) {
            real = new HighResImage(fileName);     // load from disk, but only the first time
        }
        real.show();                                // every other time, this reuses the image already loaded
    }
}
```

The page calls `show()` on a `LazyImage` exactly as it would on a real one. The first call loads the file from disk; every call after that just shows the image that is already loaded.

Proxies are also used to check permissions before a call, to cache results, and to make a call to another server look like an ordinary method call.

**Proxy or Decorator?** The code looks almost the same. The difference is the reason it exists: a decorator *adds a feature* to an object it was given, while a proxy *controls access* to the real object, and often creates that object itself.

**Watch out:** a proxy can hide slow work behind what looks like an ordinary method call. Two well-known surprises in Java projects:

- Hibernate loads related data through proxies, so a simple getter inside a loop can quietly run one database query per item.
- Spring's `@Transactional` works through a proxy. When a method calls another `@Transactional` method *on the same object*, the call skips the proxy, and the transaction setting is silently ignored.

### The other three structural patterns

These come up less often, but you should recognize them:

| Pattern | What it does | Example |
|---|---|---|
| **Composite** | Lets you treat a single item and a group of items through the same interface, so your code never needs to ask "is this one item, or many?" A group can even contain smaller groups inside it. | A shopping cart where a bundle of products has a `price()` method, just like a single product does; the bundle's price simply adds up its contents. Folders work the same way: a folder's size is the sum of the files and folders inside it. |
| **Bridge** | Splits one class hierarchy into two independent ones, so each can grow on its own instead of needing one class per combination. | A notification has a type, such as an alert or a daily digest, and a channel, such as email or SMS. Without Bridge, supporting both means a class per combination: `AlertEmail`, `AlertSms`, `DigestEmail`, `DigestSms`. With Bridge, the two vary independently, so adding a new channel does not touch the notification types. |
| **Flyweight** | Lets many small objects share the same data instead of each keeping its own copy, to save memory. | A text editor showing a million letters does not create a million separate font objects; every letter using the same font points to one shared font object. `Integer.valueOf()` does something similar: it reuses one shared object for small numbers instead of creating a new one each time. |

---

## 5. Using patterns in practice

### Telling look-alike patterns apart


Several patterns produce code that looks almost identical. What actually separates them is *why* the extra class exists, not what it looks like. Interviewers like asking about these pairs, because answering well shows that you understand a pattern's purpose, not just its shape.

| These look alike | The difference that matters |
|---|---|
| Decorator vs Proxy | Both wrap an object and offer the same interface it does. The difference is where the real object comes from, and why the wrapper exists. A decorator is *handed* an object that already exists, and its whole job is to add one feature around it, such as retrying or logging. A proxy usually *creates, guards, or locates* the real object itself, and its job is to control access to it, such as delaying creation until it is actually needed. If you are adding a feature to something you were given, it is a decorator. If you are deciding whether, when, or how the real object is reached, it is a proxy. |
| Adapter vs Facade | Both sit in front of other code, but they solve different problems. An adapter deals with *one* existing class whose interface is wrong for your code, and its job is purely translation: same one thing in, same one thing out, just reshaped. A facade sits in front of *several* classes and gives callers one simple method that does the coordinating for them. If you are reshaping one interface, it is an adapter. If you are hiding a multi-step process behind one call, it is a facade. |
| Factory Method vs simple factory | Both create an object without the caller writing `new`. A simple factory is just one method with a branch, or a lookup, that returns different classes based on its input, such as `SenderFactory.forChannel(EMAIL)`. Factory Method is a specific design where a *subclass* overrides one creation step inside a larger algorithm that the parent class controls, as in the `Delivery` example earlier on this page. If there is no subclass overriding a creation step, it is a simple factory, not Factory Method, even if both create objects from a parameter. |
| Factory Method vs Abstract Factory | Factory Method creates *one* object, and a subclass decides which one. Abstract Factory creates a *matching set* of several different objects, such as a button and a checkbox that must share the same visual theme. If the factory has one creation method, it is Factory Method. If it has several creation methods that must return things that work together, it is Abstract Factory. |
| Builder vs factory | A factory's job is choosing *which class* to create. A builder's job is assembling *one* class correctly, from many optional values, and checking the result before it exists. If the hard problem is "which type do I need?", that is a factory. If the hard problem is "this one object has too many optional settings to pass into a constructor", that is a builder. |
| Singleton vs one injected instance | Both result in one object being used everywhere. A Singleton enforces that only one instance can ever exist, and lets any class reach it directly without being given it. An injected instance is also created only once, but it is created at the composition root and handed to every class that needs it through its constructor. The practical difference shows up in tests: a test can swap in a fake for an injected instance, but it cannot easily replace a true Singleton, because the Singleton controls its own creation. |

### Justify your choice in one sentence


!!! abstract "The decision template: memorize this"
    Given **expected change X**, use **pattern A** instead of **simpler option B**, because it keeps that change **inside C**. It costs **D**. Prove it with **test E**, and revisit when **F** happens.

Two worked instances:

> Given **a second payment provider signed for next quarter**, use **an Adapter per provider behind a `PaymentGateway` interface** instead of **calling the Stripe SDK from checkout**, because a new provider becomes **one new adapter plus one registry entry**. It costs **a translation layer, including error mapping**. Prove it with **one shared set of tests that every adapter must pass**. Revisit if **providers start needing different checkout flows**, not just different APIs.

> Given **retry and audit needed on some gateways but not others**, use **Decorators** instead of **a `BaseGateway` superclass with on/off flags**, because each concern **composes independently, in a chosen order**. It costs **a deeper stack trace, and an order that must be documented**. Prove it with **a test asserting one audit entry per attempt**. Revisit if **the chain grows past three or four wrappers**.

### How patterns fail in practice

| What went wrong | How to fix it |
|---|---|
| A factory that only ever builds one kind of object. You can tell because it has a single branch, and it has never grown a second one. | Inline it, and use a plain constructor instead. Only bring a factory back if a second variant genuinely arrives. |
| A singleton holding mutable state. This shows up as flaky tests that depend on run order, or race conditions under load. | Make the state immutable, or create one instance at the composition root and pass it in, instead of reaching it through global access. |
| Decorators wrapped in the wrong order. Audit logs, metrics, or caches end up with the wrong number of entries. | Reorder the chain, add a test that pins the correct order, and build every chain in one place so the order is only decided once. |
| A wrapper chain too deep to follow. Stack traces run five or more layers deep, and nobody can say what each layer does. | Remove wrappers that add no real value, or merge closely related ones. Every remaining wrapper's name should say what it does. |
| An adapter that leaks vendor types. SDK classes start appearing in your own code, outside the adapter. | Map every vendor type to your own types inside the adapter, and keep SDK imports out of the rest of the codebase. |
| An adapter that misreports errors. Callers see success for something that was actually declined or only partly done. | Map every provider outcome explicitly, including timeouts, and test every adapter against the same list of expected results. |
| A facade that turned into a god class. Business rules and `if` statements keep piling up inside it. | Push each rule back into the subsystem class that owns it. A facade's methods should read like a short, plain list of steps. |
| A shallow prototype copy. Changing the copy also silently changes the original. | Copy every mutable part explicitly, and add a test that changes the copy and checks the original is unaffected. |
| A proxy that hides cost. Latency spikes or a burst of small queries trace back to an ordinary-looking getter. | Load eagerly where it matters, batch the calls, or at least document anything that may be slow. |

!!! warning "Collapse patterns that absorb nothing"
    A pattern is justified by the change it contains. If that change never arrived and is no longer expected, replace the pattern with the simpler code it was protecting. Removing a pattern is as much a design skill as adding one.

---

## 6. Worked example: payment gateway

**Prompt:** "Design the classes that let checkout charge customers through payment providers that differ by country."

### Questions to ask before designing anything

Before writing any class, pin down what the design actually needs to handle. Here are the answers this worked example assumes:

| Question | Assumed answer |
|---|---|
| Which providers are needed now, and which are coming? | Stripe now, and Adyen for Germany next quarter, which is reason enough to put a `PaymentGateway` interface in front of both. |
| Does the provider depend on the customer's country? | Yes, by billing country, so the gateway must be chosen at runtime. |
| Which failures are worth retrying, and is it safe to repeat a charge? | Only timeouts and rate limits. An idempotency key makes a repeated charge safe. |
| What must be audited: every attempt, or just every successful charge? | Every attempt, so it can be reconciled against the provider's own records. This is also what decides the decorator order later. |
| Can the provider's SDK types appear in our own code? | No. SDK types must stay inside the adapters. |

**Scope.** *In:* choosing a provider by country, building a valid charge request, charging, retrying temporary failures, auditing every attempt, and returning a clear result. *Out:* refunds, payouts, fraud models, and the checkout UI.

![Payment gateway composed from facade, builder, simple factory, decorators, and adapter](assets/topic-03/payment_gateway_architecture.png)

### Patterns in the design

| Design element | Pattern | Change it absorbs | Cost or guardrail |
|---|---|---|---|
| `PaymentService.pay(order)` | Facade | Checkout stays the same when fraud, tax, or ledger steps change. | It must orchestrate only; rules stay in the subsystem classes. |
| `ChargeRequest.builder()` | Builder | New optional fields, like metadata or a statement descriptor, need no new constructors. | `build()` must check every rule, such as a positive amount and a present idempotency key. |
| `GatewayRegistry.forCountry(...)` | Simple factory | A new country or provider is one new registry entry. | It must fail clearly for unsupported countries instead of returning `null`. |
| `RetryingGateway` | Decorator | Retry rules change without touching any provider code. | Retry only temporary failures, and only because the idempotency key prevents double charges. |
| `AuditingGateway` | Decorator | Audit can be added, changed, or removed per provider. | It sits **inside** retry, so every attempt is recorded. |
| `StripeAdapter`, `AdyenAdapter` | Adapter | A provider's SDK can change or be replaced behind one class. | Every provider outcome, including errors, maps to our `ChargeResult`. |

`GatewayRegistry` is a **simple factory**, not Factory Method: nothing here is a subclass choosing which object to create. It is one method, `forCountry(country)`, that picks the right gateway for its input from a map, the same way `SenderFactory.forChannel(EMAIL)` did back in section 3.

### Core code

`StripeAdapter` and `PaymentService` are unchanged from section 4. `AdyenAdapter` is left out because it has the same shape as `StripeAdapter`, just for a different provider. Three classes are new: `AuditingGateway`, `RetryingGateway` (the same class built in section 4's Decorator example), and `GatewayRegistry`.

```java
interface PaymentGateway { ChargeResult charge(ChargeRequest request); }

final class AuditingGateway implements PaymentGateway {
    private final PaymentGateway inner;
    private final AuditLog audit;
    AuditingGateway(PaymentGateway inner, AuditLog audit) { this.inner = inner; this.audit = audit; }

    public ChargeResult charge(ChargeRequest request) {
        ChargeResult result = inner.charge(request);
        audit.record(request.idempotencyKey(), result);       // one entry per attempt (it sits inside retry)
        return result;
    }
}

final class RetryingGateway implements PaymentGateway {
    private final PaymentGateway inner;

    RetryingGateway(PaymentGateway inner) {
        this.inner = inner;
    }

    public ChargeResult charge(ChargeRequest request) {
        for (int attempt = 1; attempt <= 3; attempt++) {
            ChargeResult result = inner.charge(request);
            if (!result.isTimeout()) {
                return result;
            }
        }
        return ChargeResult.declined("gateway timed out 3 times");
    }
}

final class GatewayRegistry {
    private final Map<Country, PaymentGateway> byCountry;
    GatewayRegistry(Map<Country, PaymentGateway> byCountry) { this.byCountry = Map.copyOf(byCountry); }

    PaymentGateway forCountry(Country country) {
        PaymentGateway gateway = byCountry.get(country);
        if (gateway == null) throw new UnsupportedCountryException(country);
        return gateway;
    }
}

// Composition root: the only place that knows the concrete classes and the wrapper order
PaymentGateway withPolicies(PaymentGateway adapter) {
    return new RetryingGateway(new AuditingGateway(adapter, auditLog));   // retry outside, audit inside
}
PaymentGateway stripe = withPolicies(new StripeAdapter(stripeClient));
PaymentGateway adyen  = withPolicies(new AdyenAdapter(adyenClient));
GatewayRegistry gateways = new GatewayRegistry(Map.of(US, stripe, IN, stripe, DE, adyen));
```

Three things in the code above are worth pointing out:

- `withPolicies` builds the whole decorator chain in one place. Both `stripe` and `adyen` are wrapped the same way, so the order (retry outside, audit inside) is written down once, instead of being copied for every provider.
- `GatewayRegistry` copies the map it is given, and throws `UnsupportedCountryException` instead of returning `null` for a country it does not know. A missing country is caught on the very first request, not as a `NullPointerException` deep inside checkout.
- There is no Proxy in this design, and that is deliberate. Nothing here needs to control *when* or *whether* the real gateway is created, so adding a proxy would only be adding a class to use the name.

**Failure path.** Here is what happens when a charge does not succeed on the first try:

1. Stripe times out, and `StripeAdapter` turns that into a retryable `ChargeResult`.
2. `AuditingGateway` records the attempt, then passes the result up.
3. `RetryingGateway` tries again, using the **same request**, so Stripe sees the same idempotency key and treats the retry as the same charge, not a new one.
4. A declined card is different: it is a permanent failure, so it is audited once and returned immediately, with no retry.

This only works if every adapter classifies failures the same way. If one adapter ever reported a decline as a success, every decorator above it would pass that wrong answer straight through. That is why every adapter should be tested against the same expected results, such as "a timeout is retryable" and "a decline is permanent".

### Change walkthrough

| Change request | What you edit | What you add | What stays untouched |
|---|---|---|---|
| Add Adyen for German customers. | One registry entry in the composition root. | An `AdyenAdapter` class, tested against the same expected results as the Stripe one. | Checkout, the facade, both decorators, and the Stripe adapter. |
| Add a circuit breaker for a flaky provider. | The `withPolicies` wiring. | A `CircuitBreakingGateway` decorator. | Every adapter and the facade. |
| Upgrade to a new Stripe SDK version. | `StripeAdapter` only. | Nothing. | Everything else. |
| Record latency metrics per provider. | The `withPolicies` wiring. | A `MetricsGateway` decorator. | Every adapter and the facade. |
| Add a fraud check before charging. | `PaymentService`, because the workflow itself changes. | A `FraudCheck` subsystem class. | The gateway chain and its contract. |

The last row matters. A new step in the workflow is exactly what the facade is supposed to absorb, so editing it is correct, not a design failure. Patterns protect the changes you anticipated, and saying so is a stronger answer than claiming the design handles everything.

---

## 7. Anti-patterns that cost points

- Naming a pattern ("I'll use a Strategy here") without saying which change it absorbs.
- Using a Singleton for anything that holds mutable state.
- Calling every factory "Factory Method".
- Building an Abstract Factory for a family that has only one member.
- Wrapping a decorator around every class "for flexibility".
- Letting vendor SDK types leak past the adapter.
- Hiding network calls behind proxies with no timeout and no documentation.
- Claiming a design is "open to any future change".

---

## 8. Key takeaways

- **Start from the expected change, never from the pattern.** If you cannot name the change a pattern absorbs, plain code is the right answer.
- **Every pattern has a cost.** It adds classes, and an extra step for everyone reading the code. Its value is the one change it makes cheap, plus a shared vocabulary for describing designs.
- **Create objects at the composition root, and inject them.** Classes receive what they need through their constructors, instead of calling `new` or reaching for globals. This is what makes every other pattern swappable and testable.
- **Pick a creational pattern by the problem it solves.** Use constructors and static factories first. Use Factory Method when a subclass chooses which object to create inside fixed steps, Abstract Factory when several objects must always match, Builder for many optional fields validated once in `build()`, and Prototype when copying beats building, copying mutable state deeply. Prefer one injected instance over a Singleton.
- **Pick a structural pattern by the problem it solves.** An Adapter translates one wrong interface, including its errors, and keeps vendor types at the edge. A Decorator adds one feature, in a deliberate and tested order. A Facade gives one simple entry point and holds no business rules. A Proxy controls access to the real object, and must not hide what that access costs.
- **Tell look-alike patterns apart by intent, not code shape.** Decorator and Proxy, or Adapter and Facade, can look identical. Why the extra class exists is what separates them.
- **Justify every pattern in one sentence.** "Given change X, use pattern A instead of simpler option B, because it keeps that change inside C. It costs D. Prove it with test E, and revisit when F happens."
- **Patterns fail in recognizable ways.** Watch for a factory with only one product, a singleton holding mutable state, decorators in the wrong order, an adapter that leaks vendor types or misreports errors, a facade that became a god class, and shallow copies.
- **Removing a pattern is as much a design skill as adding one.** Patterns are vocabulary for trade-offs that already exist. Show the simpler design you would use if the expected change never arrived.
