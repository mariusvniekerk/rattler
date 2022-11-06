use rattler::repo_data::OwnedLazyRepoData;
use rattler::solver::Index;
use rattler::{
    repo_data::fetch::{terminal_progress, MultiRequestRepoDataBuilder},
    virtual_packages::DETECTED_VIRTUAL_PACKAGES,
    Channel, ChannelConfig, MatchSpec,
};

#[derive(Debug, clap::Parser)]
pub struct Opt {
    #[clap(short)]
    channels: Option<Vec<String>>,

    #[clap(required = true)]
    specs: Vec<String>,
}

pub async fn create(opt: Opt) -> anyhow::Result<()> {
    let channel_config = ChannelConfig::default();

    // Parse the match specs
    let specs = opt
        .specs
        .iter()
        .map(|spec| MatchSpec::from_str(spec, &channel_config))
        .collect::<Result<Vec<_>, _>>()?;

    // Get the cache directory
    let cache_dir = dirs::cache_dir()
        .ok_or_else(|| anyhow::anyhow!("could not determine cache directory for current platform"))?
        .join("rattler/cache");
    std::fs::create_dir_all(&cache_dir)
        .map_err(|e| anyhow::anyhow!("could not create cache directory: {}", e))?;

    // Get the channels to download
    let channels = opt
        .channels
        .unwrap_or_else(|| vec![String::from("conda-forge")])
        .into_iter()
        .map(|channel_str| Channel::from_str(&channel_str, &channel_config))
        .collect::<Result<Vec<_>, _>>()?;

    // Download all repo data from the channels and create an index
    let repo_data_per_source = MultiRequestRepoDataBuilder::default()
        .set_cache_dir(&cache_dir)
        .set_listener(terminal_progress())
        .set_fail_fast(false)
        .add_channels(channels)
        .request::<OwnedLazyRepoData>()
        .await;

    // Error out if fetching one of the sources resulted in an error.
    let repo_data = repo_data_per_source
        .into_iter()
        .map(|(channel, _, result)| result.map(|data| (channel, data)))
        .collect::<Result<Vec<_>, _>>()?;

    // Construct an index
    let mut index = Index::new(
        repo_data
            .iter()
            .map(|(_c, repo_data)| repo_data.repo_data()),
        channel_config.clone(),
    );

    // Add virtual packages
    for package in DETECTED_VIRTUAL_PACKAGES.iter() {
        index.add_package(package.clone().into());
    }

    match index.solve(specs) {
        Err(e) => {
            eprintln!("Failed to solve:\n{e}");
        }
        Ok(mut result) => {
            result.sort_by(|a, b| a.name.cmp(&b.name));
            for result in result {
                eprintln!("{result}");
            }
        }
    }

    // let solver_problem = SolverProblem {
    //     channels: repo_data
    //         .iter()
    //         .map(|(channel, repodata)| (channel.base_url().to_string(), repodata))
    //         .collect(),
    //     specs,
    // };
    //
    // let result = solver_problem.solve()?;
    // println!("{:#?}", result);

    Ok(())
}