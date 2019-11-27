let userId = -1;

// -------------------- Recommendation stuff
const recommendWidget = $("#recommended-book-widget")
recommendWidget.detach()

function highlightStars(stars, ii, active) {
    const img = "/static/images/" + (active ? "fullstar.png" : "whitestar.png")
    const whitestar = "/static/images/whitestar.png"
    for (let j = 0; j < stars.length; ++j) {
        stars[j].setAttribute("src", j <= ii ? img : whitestar)
    }
}

function bindRatingEvents(book, widget) {
    const starContainer = widget.find(".rating")
    const stars = starContainer.find(".star").toArray()

    starContainer.mouseout(() => highlightStars(stars, 5, false))

    for (const [ii, star] of stars.entries()) {
        star.addEventListener("mouseover", () => highlightStars(stars, ii, true))
        star.addEventListener("mouseoff", () => highlightStars(stars, ii, false))
        star.addEventListener("click", () => {
            book.rating = ii+1

            // Tell server we've rating it rating
            $.ajax({
                url: `/addrating/${userId}/${book.id}/${book.rating}`,
                success: generateRecommendations
            })

            addToRatedBooksList(book)
        })
    }
}

function createBookWidget(book) {
    const newWidget = recommendWidget.clone()

    newWidget.find(".book-title").text(book.title)
    newWidget.find(".book-desc").html(book.desc)
    newWidget.find(".book-image").attr("src", book.image_url)

    if (book.rating === undefined) {
        newWidget.find(".remove-rating").remove()
    }

    bindRatingEvents(book, newWidget)

    return newWidget
}

function addToRatedBooksList(book) {
    const widget = createBookWidget(book)

    $("#rated-books").append(widget)
}

function generateRecommendations() {
    if (userId === -1) { return }

    const recommendedBooksDiv = $("#recommended-books")

    $.ajax({
        url: `/recommend/${userId}`,

        success: newBooks => {
            recommendedBooksDiv.empty()

            newBooks.map(createBookWidget)
                .forEach(domNode => recommendedBooksDiv.append(domNode))
        }
    })
}

// -------------------- Login / Logout Stuff
const navRegister = $("#register"), navLogin = $("#navbar-login"), navLogout = $("#navbar-logout")

navLogout.detach()

function loginWithId(id) {
    userId = id
    navLogin.detach()
    navRegister.text(`You are logged in as user id: ${userId}`)
    $("#navbarList").append(navLogout)

    generateRecommendations()
}

navRegister.click(() => {
    if (userId > 0) { return }

    $.ajax({
        url: "/register",
        success: response => loginWithId(response.new_id)
    })
})

navLogout.click(() => {
    userId = -1
    navRegister.text("Register")
    navLogout.detach()
    $("#navbarList").append(navLogin)
})

$("#modal-login-button").click(() => {
    if (userId > 0) { return }

    const loginId = parseInt($("#user-id-input").val())

    if (isNaN(loginId)) {
        alert(`Login id must be a number`)
        return
    }

    loginWithId(loginId)
    $("#modalLoginForm").modal('toggle')
})