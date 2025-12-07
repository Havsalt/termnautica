import charz_rust
import charz
from charz.typing import Char, FileLike, TextureNode
from charz._screen import ColorChoice
from colex import RESET, NONE, ColorValue


class FastSplitScreen(charz.Screen):
    def __init__(
        self,
        width: int = 16,
        height: int = 12,
        *,
        auto_resize: bool = False,
        initial_clear: bool = True,
        final_clear: bool = True,
        hide_cursor: bool = True,
        transparency_fill: Char = " ",
        stream: FileLike[str] | None = None,
        margin_right: int = 1,
        margin_bottom: int = 1,
        second_camera: charz.Camera,  # Required
        delimiter: str = "|",
        delimiter_color: ColorValue | None = None,
        delimiter_offset: int = 0,
    ) -> None:
        super().__init__(
            width,
            height,
            auto_resize=auto_resize,
            initial_clear=initial_clear,
            final_clear=final_clear,
            hide_cursor=hide_cursor,
            transparency_fill=transparency_fill,
            # NOTE: Always using ANSI until fix in `charz-rust`
            color_choice=ColorChoice.ALWAYS,
            stream=stream,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
        )
        self.second_camera = second_camera
        self.delimiter = delimiter
        self.delimiter_color = delimiter_color
        self.delimiter_offset = delimiter_offset
        self._screen_1 = charz_rust.RustScreen()
        self._screen_2 = charz_rust.RustScreen()
        self._composed_buffer = list[str]()

    def _resize_inner_screens(self) -> None:
        self._screen_1.height = self.height
        self._screen_2.height = self.height

        delimiter_len = len(self.delimiter)
        left_delimiter_len = delimiter_len // 2
        rest_delimiter_len = delimiter_len - left_delimiter_len
        left_screen_width = self.width // 2 - left_delimiter_len
        right_screen_width = self.width // 2 - rest_delimiter_len
        # There might be missing 1 cell because of `// 2`, so add it if needed
        total_width = left_screen_width + delimiter_len + right_screen_width
        diff = self.width - total_width  # *Might* be `0`, and have no effect
        left_screen_width += diff

        # ?TODO: Fix margin. There is a problem in `.show()` that causes this
        self._screen_1.width = left_screen_width + self.delimiter_offset
        self._screen_2.width = right_screen_width - self.delimiter_offset

        # ?TODO: Not needed?
        self._screen_1.reset_buffer()
        self._screen_2.reset_buffer()

    def refresh(self) -> None:
        self._resize_if_necessary()
        self._resize_inner_screens()
        self.reset_buffer()
        texture_nodes = charz.Scene.current.get_group_members(
            charz.Group.TEXTURE,
            type_hint=TextureNode,
        )
        self._screen_1.render_all(texture_nodes)
        just_current_camera = charz.Camera.current
        charz.Camera.current = self.second_camera
        self._screen_2.render_all(texture_nodes)
        charz.Camera.current = just_current_camera

        buf_1 = self._screen_1._single_line_buffer.split("\n")
        buf_2 = self._screen_2._single_line_buffer.split("\n")

        self._composed_buffer.clear()
        final_delimiter_color = (
            self.delimiter_color if self.delimiter_color is not None else NONE
        )
        for line_1, line_2 in zip(buf_1, buf_2):
            self._composed_buffer.append(
                line_1 + RESET + final_delimiter_color + self.delimiter + line_2
            )
        self.show()

    def show(self) -> None:
        # NOTE: Does not use actual size until fix in `charz-rust`
        # Construct frame from screen buffer
        out = "\n".join(self._composed_buffer)
        out += RESET
        cursor_move_code = f"\x1b[{self.height - 1}A" + "\r"
        out += cursor_move_code
        # Write and flush
        self.stream.write(out)
        self.stream.flush()
