let userId = -1;

// "Internalisation"
const TEXTS = {
    "ENG": {
        "welcome-msg-1": "Find books you'd never expect to like",
        "welcome-msg-2": "We think you'd like these 3 books",
        "edit-msg-1": "Remove or edit previous ratings",
        "edit-msg-2": "Click the stars to edit your rating",
        "search-prompt": "Filter by name",
        "register": "Register",
        "navbar-login": "Login",
        "navbar-logout": "Logout",
        "remove-rating": "Remove Rating",
        "book-card-title-label": "Title:",
        "book-genre-title-label": "Genre:",
        "book-card-desc-label": "Description:",
        "loggedIn": "You are logged in as:",
        "modal-sign-in": "Sign in",
        "modal-signin-prompt": "Your User Id:"
    },
    "ESP": {
        "welcome-msg-1": "Encuentra libros que nunca esperarías gustar",
        "welcome-msg-2": "Creemos que te gustaría estos 3 libros",
        "edit-msg-1": "Eliminar o editar calificaciones anteriores",
        "edit-msg-2": "Haz clic en las estrellas para editar tu calificación",
        "search-prompt": "Filtrar por nombre",
        "register": "Registro",
        "navbar-login": "Iniciar sesión",
        "navbar-logout": "Cerrar sesión",
        "remove-rating": "Eliminar calificación",
        "book-card-title-label": "Título:",
        "book-card-genre-label": "Género:",
        "book-card-desc-label": "Descripción:",
        "loggedIn": "Has iniciado sesión como",
        "modal-sign-in": "Registrarse",
        "modal-signin-prompt": "Su ID de usuario",
        "modal-login-button": "Iniciar sesión"
    }
}

let currentLanguage = "ENG"

function internationalize(node) {
    const langDict = TEXTS[currentLanguage]
    $(node).find("*").each((_, node) => {
        let newText = langDict[node.getAttribute("id")]
        if (newText) {
            node.innerHTML = newText
        }
    })
}

const translatedText = id => TEXTS[currentLanguage][id]

$("#nav-page-lang").click(() => {
    currentLanguage = currentLanguage === "ENG" ? "ESP" : "ENG";

    $("#page-lang").text(currentLanguage)
    $("#flag-img").attr("src", `/static/images/${currentLanguage}.png`)

    internationalize(document.body)
})

// -------------------- Recommendation stuff
const recommendWidget = $("#recommended-book-widget")
recommendWidget.detach()

function highlightStars(widget, rating, active) {
    const starImages = widget.find(".rating").children()

    const img = "/static/images/" + (active ? "fullstar.png" : "whitestar.png")
    const whitestar = "/static/images/whitestar.png"
    for (let ii = 0; ii < starImages.length; ++ii) {
        console.log(img)
        starImages[ii].setAttribute("src", ii < rating ? img : whitestar)
    }
}

function bindUnratedBookEvents(book, widget) {
    const starContainer = widget.find(".rating")
    const stars = starContainer.find(".star").toArray()

    starContainer.mouseout(() => highlightStars(widget, 5, false))

    for (const [starId, starDom] of stars.entries()) {
        const star = $(starDom), rating = starId + 1

        star.mouseover(() => highlightStars(widget, rating, true))
        star.mouseout(() => highlightStars(widget, rating, false))

        star.click(() => {
            book.rating = rating

            $.ajax({
                url: `/addrating/${userId}/${book.id}/${book.rating}`,
                success: generateRecommendations
            })

            $("#prev-rated-books").append(createBookWidget(book))
            widget.remove()
        })

    }
}

function bindRatedBookEvents(book, widget) {
    const starContainer = widget.find(".rating")
    const stars = starContainer.find(".star").toArray()

    for (const [starId, starDom] of stars.entries()) {
        const star = $(starDom), rating = starId + 1

        star.click(() => {
            $.ajax({
                url: `/changerating/${userId}/${book.id}/${rating}`
            })

            highlightStars(widget, rating, true)
        })
    }

    widget.find(".remove-rating").click(() => {
        $.ajax({
            url: `/removerating/${userId}/${book.id}/${book.rating}`
        })

        widget.remove()
    })

}

function createBookWidget(book) {
    const newWidget = recommendWidget.clone()

    newWidget.find(".book-title").text(book.title)
    newWidget.find(".book-genre").text(book.genre)
    newWidget.find(".book-desc").html(book.desc)
    newWidget.find(".book-image").attr("src", book.image_url)

    if (book.rating === undefined) {
        newWidget.find(".remove-rating").remove()
        bindUnratedBookEvents(book, newWidget)
    } else {
        highlightStars(newWidget, book.rating, true)
        bindRatedBookEvents(book, newWidget)
    }

    internationalize(newWidget)

    return newWidget
}

function loadBooksInto(container, books) {
    console.log("Got Books")
    console.log(books)
    container.empty()

    books.map(createBookWidget)
        .forEach(domNode => container.append(domNode))

    searchBarChanged()
}

function generateRecommendations() {
    if (userId === -1) {
        return
    }

    $.ajax({
        url: `/recommend/${userId}`,
        success: newBooks => loadBooksInto($("#recommended-books"), newBooks)
    })
}

// -------------------- Searhbar
const searchBar = $("#search-query")

function searchBarChanged() {
    const query = searchBar.val()

    $("#prev-rated-books").children().each((_, node) => {
        const title = $(node).find(".book-title").text()

        const flexVal = title.includes(query) ? "flex" : "none"
        console.log("foobar", flexVal)

        $(node).css("display", flexVal)
    })
}

searchBar.on('input', searchBarChanged)

// -------------------- Login / Logout Stuff
const navRegister = $("#register"), navLogin = $("#navbar-login"), navLogout = $("#navbar-logout")

navLogout.css("display", "none")

function loginWithId(id) {
    userId = id
    navLogin.css("display", "none")
    navRegister.text(translatedText('loggedIn') + userId)
    navLogout.css("display", "block")

    $.ajax({
        url: `/loadratedbooks/${userId}`,
        success: books => loadBooksInto($("#prev-rated-books"), books)
    })

    generateRecommendations()
}

navRegister.click(() => {
    if (userId > 0) {
        return
    }

    $.ajax({
        url: "/register",
        success: response => loginWithId(response.new_id)
    })
})

navLogout.click(() => {
    userId = -1
    navRegister.text(translatedText("register"))
    navLogout.css("display", "none")
    navLogin.css("display", "block")
    $("#recommended-books").empty()
    $("#prev-rated-books").empty()
})

$("#modal-login-button").click(() => {
    if (userId > 0) {
        return
    }

    const loginId = parseInt($("#user-id-input").val())

    if (isNaN(loginId)) {
        alert(`Login id must be a number`)
        return
    }

    loginWithId(loginId)
    $("#modalLoginForm").modal('toggle')
})


