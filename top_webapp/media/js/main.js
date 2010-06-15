function exclude_author(author)
{
    $.ajax({
        type: "POST",
        url: "/exclude-author/",
        data: "author="+author,
        success: exclude_author_success
    });
}

function exclude_author_success(ret)
{
    if (ret=="ok")
    {
        window.location.reload()
    }
}

function return_author(author)
{
    $.ajax({
        type: "POST",
        url: "/return-author/",
        data: "author="+author,
        success: return_author_success
    })
}

function return_author_success(ret)
{
    if (ret=="ok")
    {
        window.location.reload()
    }
}

function exclude_post(link)
{
    $.ajax({
        type: "POST",
        url: "/exclude-post/",
        data: "link="+link,
        success: exclude_post_success
    });
}

function exclude_post_success(ret)
{
    if (ret=="ok")
    {
        window.location.reload()
    }
}

function return_post(link)
{
    $.ajax({
        type: "POST",
        url: "/return-post/",
        data: "link="+link,
        success: return_post_success
    })
}

function return_post_success(ret)
{
    if (ret=="ok")
    {
        window.location.reload()
    }
}
