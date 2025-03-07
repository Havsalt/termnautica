use pyo3::prelude::*;
use rayon::prelude::*;

const RESET: &str = "\x1b[0m";

#[pyfunction]
fn render_all(
    screen: &PyAny,
    nodes: &PyAny,
    camera: &PyAny,
    camera_centering_x: f32,
    camera_centering_y: f32,
) -> PyResult<String> {
    let screen_width: u32 = screen.getattr("width")?.extract()?;
    let screen_height: u32 = screen.getattr("height")?.extract()?;
    let camera_position = camera.getattr("global_position")?;
    let mut camera_x: f32 = camera_position.getattr("x")?.extract()?;
    camera_x -= camera_centering_x;
    let mut camera_y: f32 = camera_position.getattr("y")?.extract()?;
    camera_y -= camera_centering_y;
    let transparency_fill: char = screen.getattr("transparancy_fill")?.extract()?;
    // Empty 2D screen buffer filled with `screen.transparency_fill`
    let mut screen_buf: Vec<Vec<(char, Option<String>)>> =
        vec![vec![(transparency_fill, None); screen_width as usize]; screen_height as usize];
    let nodes_list: Vec<&PyAny> = nodes.extract()?;
    let mut nodes_z_index_pairs: Vec<_> = nodes_list
        .iter()
        .map(|node| {
            let z_index = node.getattr("z_index").unwrap().extract::<i32>().unwrap();
            (node, z_index)
        })
        .collect();
    nodes_z_index_pairs.sort_unstable_by(|(_, a), (_, b)| a.cmp(b));

    // Render each `TextureNode`
    for (node, z_index) in nodes_z_index_pairs {
        let is_globally_visible_meth = node.getattr("is_globally_visible")?;
        if !is_globally_visible_meth.call0()?.extract()? {
            continue;
        }
        let global_position = node.getattr("global_position")?;
        let global_x: f32 = global_position.getattr("x")?.extract()?;
        let global_y: f32 = global_position.getattr("y")?.extract()?;
        let rel_x = global_x - camera_x;
        let rel_y = global_y - camera_y;
        let global_rotation: f32 = node.getattr("global_rotation")?.extract()?;
        let texture: Vec<String> = node.getattr("texture")?.extract()?;
        let node_transparency: Option<char> = node.getattr("transparency")?.extract()?;
        let color: Option<String> = node.getattr("color")?.extract()?;

        for (h, row) in texture.iter().enumerate() {
            let final_y = rel_y + (h as f32);
            let row_index = f32::floor(final_y) as i32;
            if 0 > row_index || row_index >= (screen_height as i32) {
                continue;
            }
            for (w, cell) in row.chars().enumerate() {
                let final_x = rel_x + (w as f32);
                let cell_index = f32::floor(final_x) as i32;
                if 0 > cell_index || cell_index >= (screen_width as i32) {
                    continue;
                }
                if let Some(transparency_char) = node_transparency {
                    if cell == transparency_char {
                        continue;
                    }
                }
                screen_buf[row_index as usize][cell_index as usize] = (cell, color.clone());
            }
        }
    }

    // Convert 2D `Vec` of `char` to `String` joined with "\n"
    let out = screen_buf
        .iter()
        .map(|line_buf| {
            line_buf
                .iter()
                .map(|(cell, color)| {
                    if let Some(color_code) = color {
                        format!("{RESET}{color_code}{cell}")
                    } else {
                        format!("{RESET}{cell}")
                    }
                })
                .collect()
        })
        .collect::<Vec<String>>()
        .join("\n");

    Ok(out)
}

#[pymodule]
fn render(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_all, m)?)?;
    Ok(())
}
