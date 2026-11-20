## BabyView webCDI wide exports -> long item-level CDI file for the paired-calibration analysis.
## Keeps only subject number, age, form and item responses: every background/demographic column
## (zip code, birth weight, caregiver info, ...) and the free-text sentence examples are dropped.
## Run locally where the webCDI exports live (standard_model_2/data/raw/babyview).
## Usage: Rscript 01_cdi_items.R <babyview_raw_dir> <out_dir>
## Output (keyed by subject_num, pseudonymised later on ccn2):
##   cdi_items_raw.csv   subject_num, age_month, form, item_kind, category, item_definition, value
##   cdi_admins_raw.csv  subject_num, age_month, form, production
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(readr)})
args <- commandArgs(trailingOnly = TRUE)
raw_dir <- args[1]; out_dir <- args[2]

dict <- bind_rows(
  read_csv(file.path(raw_dir, "webcdi_items_WG.csv"), show_col_types = FALSE) %>% mutate(form = "WG"),
  read_csv(file.path(raw_dir, "webcdi_items_WS.csv"), show_col_types = FALSE) %>% mutate(form = "WS")) %>%
  transmute(form, item_key = item, item_definition = definition, category, choices) %>%
  distinct(form, item_key, .keep_all = TRUE)

morph <- c("word_forms_verbs", "word_endings_verbs", "word_endings",
           "word_forms_nouns", "word_endings_nouns")
## vocabulary checklist = "produces"-type items outside the morphology sections
dict <- dict %>%
  mutate(is_vocab = grepl("produces", coalesce(choices, "")) & !category %in% morph,
         item_kind = case_when(category %in% morph ~ category, is_vocab ~ "word", TRUE ~ NA_character_)) %>%
  filter(!is.na(item_kind))

read_form <- function(f, form_label) {
  d <- read_csv(file.path(raw_dir, "data_june_2026", f), show_col_types = FALSE, progress = FALSE,
                col_types = cols(.default = col_character()))
  keys <- intersect(dict$item_key[dict$form == form_label], colnames(d))
  d %>% filter(completed == "TRUE" | completed == "True", !is.na(age), age != "999") %>%
    transmute(subject_num = as.integer(subject_id), age_month = as.integer(age), form = form_label,
              across(all_of(keys))) %>%
    pivot_longer(-c(subject_num, age_month, form), names_to = "item_key", values_to = "value")
}
items <- bind_rows(read_form("babyview-english-ws_items.csv", "WS"),
                   read_form("babyview-english-wg_items.csv", "WG")) %>%
  left_join(dict, by = c("form", "item_key"))

admins <- items %>% filter(is_vocab) %>%
  group_by(subject_num, age_month, form) %>%
  summarise(production = sum(value == "produces", na.rm = TRUE), .groups = "drop")

dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
items %>% select(subject_num, age_month, form, item_kind, category, item_definition, value) %>%
  write_csv(file.path(out_dir, "cdi_items_raw.csv"), na = "")
write_csv(admins, file.path(out_dir, "cdi_admins_raw.csv"))
cat(sprintf("items rows=%d admins=%d kids=%d\n", nrow(items), nrow(admins), n_distinct(admins$subject_num)))
print(count(items, form, item_kind))
