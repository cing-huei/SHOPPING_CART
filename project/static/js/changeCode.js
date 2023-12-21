function changeCode(obj)
{
    $(obj).attr('src','/shopping_app/loadCode/?r='+new Date().getTime())
}