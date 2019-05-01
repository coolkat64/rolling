pub mod zone;

extern crate num_cpus;
use crate::map::generator::zone::ZoneGenerator;
use crate::map::world::World;
use crate::tile::world::types as world_types;
use crate::tile::zone::types as zone_types;
use crate::RollingError;
use crossbeam::channel::unbounded;
use crossbeam::thread;
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::thread::sleep;
use std::time;

pub struct Generator<'a> {
    world: &'a World<'a>,
}

impl<'a> Generator<'a> {
    pub fn new(world: &'a World) -> Generator<'a> {
        Generator { world: &world }
    }
}

fn create_empty_progress(world: &World) -> String {
    let mut progress: String = String::new();
    for row in world.rows.iter() {
        for _ in row.iter() {
            progress.push_str(" ");
        }
        progress.push_str("\n");
    }
    progress
}

fn create_updated_progress(
    progress: &String,
    done_row_i: usize,
    done_col_i: usize,
    world: &World,
) -> String {
    let mut progress_vec: Vec<&str> = progress.split("\n").collect();
    let change_row = progress_vec[done_row_i];
    let mut new_row = String::new();
    for (current_str_i, current_str) in change_row.chars().enumerate() {
        if current_str_i == done_col_i {
            new_row.push_str(&world.geo_chars[done_row_i][done_col_i].to_string());
        } else {
            new_row.push_str(&current_str.to_string());
        }
    }
    progress_vec[done_row_i] = new_row.as_str();
    progress_vec.join("\n")
}

fn wait_or_run(max: usize, counter: &Arc<Mutex<usize>>) {
    let sleep_time = time::Duration::from_millis(250);
    loop {
        let mut counter_value = counter.lock().unwrap();
        if counter_value.lt(&max) {
            *counter_value += 1;
            drop(counter_value);
            break;
        } else {
            drop(counter_value);
            sleep(sleep_time);
        }
    }
}

fn decrease_counter(counter: &Arc<Mutex<usize>>) {
    let mut counter_value = counter.lock().unwrap();
    *counter_value -= 1;
    drop(counter_value);
}

impl<'a> Generator<'a> {
    pub fn generate(
        &self,
        target_folder: &Path,
        width: u32,
        height: u32,
    ) -> Result<(), RollingError> {
        println!(
            "target is {} for {} and {}",
            target_folder.display(),
            width,
            height
        );

        // Prepare progress string
        let mut progress = create_empty_progress(self.world);
        let max_concurrent_thread_count = num_cpus::get();
        let concurrent_thread_count = Arc::new(Mutex::new(0));

        println!("{}", progress);
        let (sender, receiver) = unbounded();

        thread::scope(|scope| {
            for (row_i, row) in self.world.rows.iter().enumerate() {
                for (col_i, world_tile) in row.iter().enumerate() {
                    let thread_s = sender.clone();
                    let thread_counter_mutex = Arc::clone(&concurrent_thread_count);

                    scope.spawn(move |_| {
                        wait_or_run(max_concurrent_thread_count, &thread_counter_mutex);
                        let target_path =
                            Path::new(target_folder).join(format!("{}-{}.txt", row_i, col_i));
                        let zone_generator = self.get_zone_generator(&world_tile);

                        match zone_generator.generate(target_path.as_path(), width, height) {
                            Err(e) => {
                                decrease_counter(&thread_counter_mutex);
                                return Err(RollingError::new(format!(
                                    "Error during generation of {}-{}.txt: {}",
                                    row_i, col_i, e
                                )));
                            }
                            Ok(_) => {
                                decrease_counter(&thread_counter_mutex);
                                thread_s.send((row_i, col_i)).unwrap();
                                Ok(())
                            }
                        }
                    });
                }
                println!();
            }
            drop(sender);

            for (done_row_i, done_col_i) in receiver {
                progress = create_updated_progress(&progress, done_row_i, done_col_i, self.world);
                println!("{}", progress);
            }
        })
        .unwrap();

        Ok(())
    }

    fn get_zone_generator(&self, world_tile: &world_types::WorldTile) -> impl zone::ZoneGenerator {
        match world_tile {
            world_types::WorldTile::Beach => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::Sand,
            },
            world_types::WorldTile::Sea => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::SaltedWater,
            },
            world_types::WorldTile::Mountain => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::RockyGround,
            },
            world_types::WorldTile::Plain => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::ShortGrass,
            },
            world_types::WorldTile::Jungle => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::Dirt,
            },
            world_types::WorldTile::Hill => zone::DefaultGenerator {
                world: self.world,
                default_tile: &zone_types::ZoneTile::ShortGrass,
            },
        }
    }
}
