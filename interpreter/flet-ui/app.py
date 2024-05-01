import flet as ft


def main(page: ft.Page):
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Open-Interpreter",
                icon=ft.icons.CIRCLE_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.CIRCLE),
            ),
            ft.Divider(thickness=2),
            ft.ListView(
                controls=[
                    ft.TextButton(text="chat title"),
                ],
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.MAIL_OUTLINED),
                label="Item 2",
                selected_icon=ft.icons.MAIL,
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.PHONE_OUTLINED),
                label="Item 3",
                selected_icon=ft.icons.PHONE,
            ),
        ],
    )

    def show_drawer(e):
        page.drawer.open = True
        page.drawer.update()

    page.add(ft.ElevatedButton("Show drawer", on_click=show_drawer))

ft.app(main)