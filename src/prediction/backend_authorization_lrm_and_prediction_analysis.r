suppressPackageStartupMessages(library(rms))
suppressPackageStartupMessages(library(jsonlite))

score_descriptions <- c(
  "4" = "Very Well Supported (++)",
  "3" = "Well Supported (+)",
  "2" = "Partially Supported, with serious flaws (~)",
  "1" = "Initial Support, with serious flaws (-)",
  "0" = "Not Supported (--)"
)

training_file <- "../../data/backend_authorization.csv"
prediction_file <- "../../output/stats/backend_authorization.csv"

if (!file.exists(prediction_file) || file.info(prediction_file)$size == 0) {
  cat("[Backend Authorization] Prediction failed: No input data found.\n")
} else {
  training_data_raw <- read.csv(training_file, stringsAsFactors = FALSE)
  prediction_data <- read.csv(prediction_file, stringsAsFactors = FALSE)
  training_data <- subset(training_data_raw, GT != "" & !is.na(GT))
  training_data[is.na(training_data)] <- 0
  prediction_data[is.na(prediction_data)] <- 0
  required_cols <- c("AUB_T", "AUB_P", "AUB_A")
  if (all(required_cols %in% colnames(prediction_data))) {
    training_data$GT <- factor(training_data$GT, levels = c("0", "1", "2", "3", "4"), ordered = TRUE)
    lrm_model <- lrm(GT ~ AUB_T + AUB_P + AUB_A, data = training_data, x = TRUE, y = TRUE, maxit=1000) 
    predicted_probabilities <- predict(lrm_model, prediction_data, type="fitted.ind")
    if (is.vector(predicted_probabilities)) {
      predicted_probabilities <- t(as.matrix(predicted_probabilities))
    } 
    predicted_level_name <- colnames(predicted_probabilities)[apply(predicted_probabilities, 1, which.max)]
    numeric_score <- sub("GT=", "", predicted_level_name)
    friendly_message <- score_descriptions[numeric_score]
    final_output <- paste("[Backend Authorization] Predicted Security Level:", friendly_message)
    cat(final_output)
  } else {
    missing_cols <- paste(setdiff(required_cols, colnames(prediction_data)), collapse=", ")
    cat(paste("[Backend Authorization] Prediction failed: Input data is missing required columns:", missing_cols, "\n"))
  }
}